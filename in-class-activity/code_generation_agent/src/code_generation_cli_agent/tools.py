from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Iterable, Set


class Tools:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()

    def _safe(self, rel_path: str) -> Path:
        p = (self.repo_path / rel_path).resolve()
        if not str(p).startswith(str(self.repo_path)):
            raise ValueError("Unsafe path traversal blocked.")
        return p

    def read(self, rel_path: str, max_chars: int = 20000) -> str:
        p = self._safe(rel_path)
        if not p.exists():
            return ""
        return p.read_text(encoding="utf-8", errors="replace")[:max_chars]

    def write(self, rel_path: str, content: str) -> None:
        p = self._safe(rel_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def run(self, cmd: str, timeout_s: int = 600) -> Tuple[bool, str]:
        proc = subprocess.run(
            cmd,
            cwd=self.repo_path,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        out = (out.strip() or "[NO OUTPUT]")
        return proc.returncode == 0, out[:20000]

    def git_commit(self, message: str) -> Tuple[bool, str]:
        ok1, out1 = self.run("git add -A")
        if not ok1:
            return False, out1
        safe_msg = message.replace('"', "'")
        return self.run(f'git commit -m "{safe_msg}"')

    def git_push(self) -> Tuple[bool, str]:
        return self.run("git push")

    def _collect_local_modules(self, roots: Iterable[Path]) -> Set[str]:
        """Return module/package names that exist locally under the roots."""
        local: Set[str] = set()
        for root in roots:
            if not root.exists():
                continue

            if root.is_file() and root.suffix == ".py":
                local.add(root.stem)
                continue

            # Local single-file modules
            for py in root.rglob("*.py"):
                local.add(py.stem)

            # Local packages (directories with __init__.py)
            for init in root.rglob("__init__.py"):
                pkg_dir = init.parent
                local.add(pkg_dir.name)

        # Common “don’t treat as pip deps”
        local.update({"__init__"})
        return local

    def generate_requirements_txt_from_imports(
        self,
        out_rel_path: str,
        scan_rel_paths: Iterable[str],
    ) -> str:
        imports: Set[str] = set()

        roots: list[Path] = []
        for rel in scan_rel_paths:
            p = self._safe(rel)
            roots.append(p)

            if not p.exists():
                continue

            py_files = [p] if p.is_file() and p.suffix == ".py" else list(p.rglob("*.py"))
            for py_file in py_files:
                try:
                    text = py_file.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(text)
                except Exception:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            name = (alias.name or "").split(".")[0].strip()
                            if name:
                                imports.add(name)
                    elif isinstance(node, ast.ImportFrom):
                        # Skip relative imports like: from .utils import x
                        if getattr(node, "level", 0) and node.level > 0:
                            continue
                        if node.module:
                            name = node.module.split(".")[0].strip()
                            if name:
                                imports.add(name)

        stdlib = set(getattr(sys, "stdlib_module_names", set()))
        local_modules = self._collect_local_modules(roots)

        # Remove stdlib + local project modules
        imports = {
            m for m in imports
            if m and m not in stdlib and m not in local_modules and m not in {"__future__", "typing"}
        }

        mapping = {
            "yaml": "PyYAML",
            "bs4": "beautifulsoup4",
            "PIL": "Pillow",
            "cv2": "opencv-python",
        }

        reqs = sorted(mapping.get(m, m) for m in imports)
        content = "\n".join(reqs).strip() + ("\n" if reqs else "")
        self.write(out_rel_path, content)
        return content