from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest
from importlib.metadata import version as dist_version

import hotdata_marimo as hm


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "hotdata_marimo"
_RUNTIME_SUBMODULE = re.compile(
    r"(?m)^\s*(?:from\s+hotdata_runtime\.(client|env|result|health)\s+import"
    r"|import\s+hotdata_runtime\.(client|env|result|health)(?:\s|$|,|as))"
)


def test_version_is_pep440_core():
    assert re.fullmatch(r"\d+\.\d+\.\d+(\+.*)?", hm.__version__)


def test_version_matches_distribution_metadata():
    assert dist_version("hotdata-marimo") == hm.__version__


@pytest.mark.parametrize("name", hm.__all__)
def test_public_export_is_importable(name: str):
    assert hasattr(hm, name), f"missing export: {name}"
    assert getattr(hm, name) is not None


def test_runtime_primitives_are_reexported():
    from hotdata_runtime import HotdataClient, QueryResult, from_env

    assert hm.HotdataClient is HotdataClient
    assert hm.QueryResult is QueryResult
    assert hm.from_env is from_env


@pytest.mark.parametrize(
    ("alias", "target"),
    [
        ("hotdata_sql_editor", "sql_editor"),
        ("hotdata_table_browser", "table_browser"),
        ("hotdata_query_result", "query_result"),
        ("hotdata_connection_picker", "connection_picker"),
        ("hotdata_workspace_selector", "workspace_selector_from_env"),
        ("hotdata_recent_results", "recent_results"),
    ],
)
def test_mo_ui_aliases_match_public_helpers(alias: str, target: str):
    assert getattr(hm, alias) is getattr(hm, target)


def test_source_uses_hotdata_runtime_root_imports():
    violations: list[str] = []
    for path in SOURCE_ROOT.rglob("*.py"):
        if _RUNTIME_SUBMODULE.search(path.read_text(encoding="utf-8")):
            violations.append(str(path.relative_to(REPO_ROOT)))
    assert not violations, (
        "Use `from hotdata_runtime import ...` in package source; "
        f"found submodule imports in: {', '.join(violations)}"
    )


def test_no_stale_submodule_surface():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("hotdata_marimo.client")
