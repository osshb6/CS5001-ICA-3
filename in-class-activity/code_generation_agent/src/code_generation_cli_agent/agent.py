from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from .llm import OllamaLLM
from .prompt_manager import PromptManager
from .tools import Tools
from .types import AgentConfig, RunResult
from .utils import strip_code_fences, parse_files_json


class Agent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.repo = Path(cfg.repo).resolve()
        self.tools = Tools(self.repo)
        self.prompt_manager = PromptManager()

        # Default prompt variants
        self.planning_variant = "default"
        self.code_gen_variant = "default"

    def _log(self, message: Any) -> None:
        if self.cfg.verbose:
            print(message)

    def _llm(self) -> OllamaLLM:
        return OllamaLLM(
            model=self.cfg.model,
            host=self.cfg.host,
            temperature=self.cfg.temperature,
        )

    def _call_llm(self, prompt: str) -> str:
        return self._llm().generate(prompt)

    def _multi_step_chain(self) -> Callable[[str], str]:
        try:
            from langchain_core.runnables import RunnableLambda
        except Exception:
            return self._call_llm
        return RunnableLambda(self._call_llm).invoke

    @staticmethod
    def _norm_rel(rel_path: str) -> str:
        return (rel_path or "").lstrip("/").replace("\\", "/").strip()

    @staticmethod
    def _relocate_into_dir(rel_path: str, target_dir: str) -> str:
        """
        Ensure rel_path is under target_dir. If it's already under target_dir, keep it.
        Otherwise, move it to target_dir/<rel_path> (preserves subdirs).

        Example:
          target_dir = "updated/calculator"
          "README.md" -> "updated/calculator/README.md"
          "src/utils.py" -> "updated/calculator/src/utils.py"
        """
        rel_path = Agent._norm_rel(rel_path)
        if target_dir in ("", "."):
            return rel_path

        prefix = target_dir.rstrip("/") + "/"
        if rel_path.startswith(prefix):
            return rel_path

        return prefix + rel_path

    def _ensure_init_chain_for_path(self, rel_py_path: str, package_root: str | None) -> None:
        """
        For a python file path like:
          updated/calculator/app.py
        ensure:
          updated/__init__.py
          updated/calculator/__init__.py

        We only create __init__.py files for directories at/under `package_root`
        (e.g., "updated"). If package_root is None, we do nothing.
        """
        rel_py_path = self._norm_rel(rel_py_path)
        if not rel_py_path.endswith(".py"):
            return
        if not package_root or package_root in ("", "."):
            return

        p = Path(rel_py_path)
        parts = p.parts

        # Only operate on paths that are inside the package_root directory.
        # E.g., if package_root="updated", require path starts with "updated/..."
        if not parts or parts[0] != package_root:
            return

        # Walk directories from package_root down to the file's parent dir.
        # For updated/calculator/app.py => create updated/__init__.py and updated/calculator/__init__.py
        accum = Path(parts[0])
        for dir_part in parts[1:-1]:  # up to parent dir
            init_rel = (accum / "__init__.py").as_posix()
            init_abs = (self.repo / init_rel).resolve()
            if not init_abs.exists():
                self.tools.write(init_rel, "")  # empty is fine
            accum = accum / dir_part

        # Also create __init__.py in the immediate parent directory of the file.
        init_rel = (accum / "__init__.py").as_posix()
        init_abs = (self.repo / init_rel).resolve()
        if not init_abs.exists():
            self.tools.write(init_rel, "")

    def _enforce_same_folder_imports(self, module_dir: str) -> None:
        """
        Rewrite package-qualified imports that assume repo root is on sys.path, into
        same-folder imports so running scripts from their folder works (e.g.:
          streamlit run updated/calculator/app.py

        Examples rewritten:
          from updated.calculator.calculator import add -> from calculator import add
          import updated.calculator.ui as ui         -> import ui as ui
          import updated.calculator.ui               -> import ui
        """
        module_dir = self._norm_rel(module_dir).strip("/")
        if not module_dir or module_dir == ".":
            return

        pkg_prefix = module_dir.replace("/", ".")  # e.g. "updated.calculator"
        root = (self.repo / module_dir).resolve()
        if not root.exists():
            return

        for py_path in root.rglob("*.py"):
            try:
                text = py_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                # If something weird happens, skip the file rather than failing the whole run.
                continue

            new_text = text

            # from updated.calculator.something import X  -> from something import X
            new_text = re.sub(
                rf"^from\s+{re.escape(pkg_prefix)}\.([a-zA-Z_]\w*)\s+import\s+",
                r"from \1 import ",
                new_text,
                flags=re.MULTILINE,
            )

            # import updated.calculator.something as s -> import something as s
            new_text = re.sub(
                rf"^import\s+{re.escape(pkg_prefix)}\.([a-zA-Z_]\w*)\s+as\s+",
                r"import \1 as ",
                new_text,
                flags=re.MULTILINE,
            )

            # import updated.calculator.something -> import something
            new_text = re.sub(
                rf"^import\s+{re.escape(pkg_prefix)}\.([a-zA-Z_]\w*)\s*$",
                r"import \1",
                new_text,
                flags=re.MULTILINE,
            )

            # Also handle: from updated.calculator import calculator -> import calculator
            new_text = re.sub(
                rf"^from\s+{re.escape(pkg_prefix)}\s+import\s+([a-zA-Z_]\w*)\s*$",
                r"import \1",
                new_text,
                flags=re.MULTILINE,
            )

            if new_text != text:
                try:
                    py_path.write_text(new_text, encoding="utf-8")
                except Exception:
                    # Don't fail the run if rewrite can't be written
                    pass

    def create_program(self, desc: str, module_path: str) -> RunResult:
        """
        Create a small project.

        Guarantees:
        - Multi-file JSON is supported
        - Everything the agent writes ends up under the entry module's directory
          (i.e., Path(module_path).parent)
        - __init__.py files are created for the package chain
        - requirements.txt is written under that same directory (unless model provided one)
        - internal imports are rewritten to same-folder imports so `streamlit run path/to/app.py` works
        """
        run = self._multi_step_chain()

        # Plan
        p1 = self.prompt_manager.get_prompt(
            "planning",
            self.planning_variant,
            desc=desc,
            module_path=module_path,
        )
        self._log(p1)
        plan = run(p1).strip()
        if not plan:
            return RunResult(False, "Model returned empty plan.")

        # Draft code (EXPECT multi-file JSON map)
        p2 = self.prompt_manager.get_prompt(
            "code_generation",
            self.code_gen_variant,
            desc=desc,
            module_path=module_path,
            plan=plan,
        )
        self._log(p2)
        draft_raw = run(p2)
        self._log(draft_raw)

        files_map: dict[str, str] | None = None
        try:
            files_map = parse_files_json(draft_raw)

            # Enforce "real" multi-file: >= 2 python files (practical minimum)
            py_files = [p for p in files_map.keys() if p.endswith(".py")]
            if len(py_files) < 2:
                return RunResult(
                    False,
                    f"Expected a multi-file project with >=2 Python files. Got {len(py_files)}: {py_files}",
                )

        except Exception as e:
            # Backward-compatible fallback: treat as a single module draft
            self._log(f"[WARN] parse_files_json failed; falling back to single-file mode: {e}")

        written_paths: list[str] = []

        # All files should live under the entry module directory
        module_dir = Path(module_path).parent.as_posix()
        auto_req_path = f"{module_dir}/requirements.txt" if module_dir not in (".", "") else "requirements.txt"

        # We'll use this to decide whether to auto-generate requirements
        model_provided_requirements_after_relocate = False

        # Package root is the first directory segment of module_path (e.g., "updated")
        module_parts = Path(self._norm_rel(module_path)).parts
        package_root = module_parts[0] if module_parts and module_parts[0] not in ("", ".") else None

        if files_map:
            # Write all files from the JSON map (relocated under module_dir)
            for rel_path, content in files_map.items():
                target_rel_path = self._relocate_into_dir(rel_path, module_dir)

                if target_rel_path == auto_req_path:
                    model_provided_requirements_after_relocate = True

                normalized = (content or "").rstrip() + "\n"
                self.tools.write(target_rel_path, normalized)
                written_paths.append(target_rel_path)

            # Ensure the requested entry module exists in the model output
            if module_path not in files_map:
                return RunResult(False, f"Model did not include entrypoint file: {module_path}")

        else:
            # Single-file fallback
            draft = strip_code_fences(draft_raw)
            if not draft.strip():
                return RunResult(False, "Model returned empty module draft.")

            final_code = draft.rstrip() + "\n"
            self.tools.write(module_path, final_code)
            written_paths.append(module_path)

        # Ensure __init__.py exists for the package chain for all written python files.
        written_py_files = [p for p in written_paths if p.endswith(".py")]
        for py_rel in written_py_files:
            self._ensure_init_chain_for_path(py_rel, package_root)

        # Rewrite imports inside module_dir to same-folder imports (fixes Streamlit path execution)
        self._enforce_same_folder_imports(module_dir)

        # Requirements behavior:
        # - If model already provided requirements.txt (after relocation), don't auto-generate.
        # - Otherwise generate into auto_req_path, scanning only module_dir (everything lives there now).
        if not model_provided_requirements_after_relocate:
            scan_targets = [module_dir] if module_dir not in (".", "") else ["."]
            self.tools.generate_requirements_txt_from_imports(
                out_rel_path=auto_req_path,
                scan_rel_paths=scan_targets,
            )
            req_note = auto_req_path
        else:
            req_note = auto_req_path  # model provided it (after relocation)

        if len(written_paths) == 1:
            return RunResult(True, f"Wrote module: {module_path} (and {req_note})")
        return RunResult(True, f"Wrote {len(written_paths)} files (entrypoint: {module_path}) and {req_note}")

    def commit_and_push(self, message: str, push: bool) -> RunResult:
        ok, out = self.tools.git_commit(message)
        if not ok:
            return RunResult(False, out)

        if push:
            ok2, out2 = self.tools.git_push()
            if not ok2:
                return RunResult(False, "Commit succeeded, but push failed:\n" + out2)
            return RunResult(True, "Commit and push succeeded.")

        return RunResult(True, "Commit succeeded.")

    def list_available_prompts(self) -> dict[str, list[str]]:
        tasks = self.prompt_manager.list_available_tasks()
        return {task: self.prompt_manager.list_variants(task) for task in tasks}
