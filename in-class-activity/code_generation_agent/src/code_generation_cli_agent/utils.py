from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict


def ensure_repo_path(repo: str) -> Path:
    p = Path(repo).resolve()

    # Create the repo directory if it does not exist.
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

    if not p.is_dir():
        raise SystemExit(f"Invalid repo path (not a directory): {repo}")

    return p


def strip_code_fences(text: str) -> str:
    if not text:
        return ""

    s = text.strip()
    s = re.sub(r"^\s*Here is the code:\s*", "", s, flags=re.IGNORECASE)
    lines = s.splitlines()

    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].lstrip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()

def parse_files_json(text: str) -> Dict[str, str]:
    """
    Parse a JSON object mapping file paths -> file contents.
    Tolerates accidental code fences.
    """
    s = (text or "").strip()
    # strip outer ``` fences if they happen
    lines = s.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].lstrip().startswith("```"):
        lines = lines[:-1]
    s = "\n".join(lines).strip()

    # try direct json
    try:
        data = json.loads(s)
        if isinstance(data, dict):
            # Must look like a "files map": keys are file paths
            pathlike_keys = [
                k for k in data.keys()
                if isinstance(k, str) and ("/" in k or k.endswith((".py", ".md", ".txt", ".yaml", ".yml", ".json")))
            ]
            if not pathlike_keys:
                raise ValueError("JSON did not look like a files map (no path-like keys).")

    except json.JSONDecodeError:
        # fallback: attempt to extract the first {...} block
        m = re.search(r"(?s)\{.*\}", s)
        if not m:
            raise ValueError("Model did not return valid JSON object for files.")
        data = json.loads(m.group(0))

    if not isinstance(data, dict):
        raise ValueError("Files JSON must be an object/dict.")

    files: Dict[str, str] = {}
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError("Files JSON keys and values must be strings.")
        files[k] = v
    return files