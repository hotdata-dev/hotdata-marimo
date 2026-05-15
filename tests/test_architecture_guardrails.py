from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "hotdata_marimo"


def test_source_uses_hotdata_runtime_root_imports() -> None:
    violations: list[str] = []
    pattern = re.compile(r"(?m)^\s*from\s+hotdata_runtime\.(client|env|result|health)\s+import")

    for path in SOURCE_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            violations.append(str(path.relative_to(REPO_ROOT)))

    assert not violations, (
        "Use `from hotdata_runtime import ...` in package source; "
        f"found submodule imports in: {', '.join(violations)}"
    )
