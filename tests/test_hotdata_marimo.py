from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import hotdata_marimo as hm
from hotdata_runtime import HotdataClient
from hotdata_marimo._options import connection_options, unique_label_options
from hotdata_marimo.display import connections_panel
from hotdata_marimo.sql_engine import HotdataMarimoEngine
from hotdata_marimo.workspace_selector import WorkspaceSelector, workspace_selector_from_env
from marimo._types.ids import VariableName


def _selection(*, workspace_id: str, source: str, workspaces: list | None = None):
    return SimpleNamespace(
        workspace_id=workspace_id,
        source=source,
        workspaces=workspaces or [],
    )


def _workspace_row(name: str, public_id: str, *, active: bool = True):
    return SimpleNamespace(name=name, public_id=public_id, active=active)


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        (
            [("dup", "a"), ("dup", "b"), ("dup", "c")],
            {"dup": "a", "dup (2)": "b", "dup (3)": "c"},
        ),
        (
            [],
            {},
        ),
    ],
)
def test_unique_label_options(labels, expected):
    assert unique_label_options(labels) == expected


def test_connection_options_disambiguates_duplicate_names():
    conns = [
        SimpleNamespace(name="Warehouse", id="conn_1"),
        SimpleNamespace(name="Warehouse", id="conn_2"),
        SimpleNamespace(name="Analytics", id="conn_3"),
    ]
    assert connection_options(conns) == {
        "Warehouse": "conn_1",
        "Warehouse (conn_2)": "conn_2",
        "Analytics": "conn_3",
    }


@pytest.mark.parametrize(
    ("resolve", "expect_dropdown", "expected_workspace"),
    [
        (
            _selection(workspace_id="ws_explicit", source="explicit_env"),
            False,
            "ws_explicit",
        ),
        (
            _selection(
                workspace_id="ws_only",
                source="active",
                workspaces=[_workspace_row("Only", "ws_only")],
            ),
            False,
            "ws_only",
        ),
        (
            _selection(
                workspace_id="ws_a",
                source="active",
                workspaces=[
                    _workspace_row("Alpha", "ws_a"),
                    _workspace_row("Beta", "ws_b", active=False),
                ],
            ),
            True,
            "ws_b",
        ),
    ],
)
def test_workspace_selector(resolve, expect_dropdown, expected_workspace):
    pick = MagicMock()
    pick.value = resolve.workspace_id
    with patch(
        "hotdata_marimo.workspace_selector.resolve_workspace_selection",
        return_value=resolve,
    ), patch(
        "hotdata_marimo.workspace_selector.mo.ui.dropdown",
        return_value=pick,
    ):
        selector = WorkspaceSelector(api_key="k")
    if expect_dropdown:
        pick.value = expected_workspace
    assert (selector._pick is not None) is expect_dropdown
    assert selector.workspace_id == expected_workspace
    assert selector.client.workspace_id == expected_workspace


def test_connections_panel_lists_connections(mock_client):
    mock_client.connections.return_value.list_connections.return_value = (
        SimpleNamespace(
            connections=[
                SimpleNamespace(
                    name="Warehouse",
                    id="conn_1",
                    source_type="postgres",
                ),
                SimpleNamespace(
                    name="Analytics",
                    id="conn_2",
                    source_type="snowflake",
                ),
            ]
        )
    )
    with patch("hotdata_marimo.display.workspace_health_lines", return_value=(True, ["ok"])):
        panel = connections_panel(mock_client)
    assert panel is not None


def test_workspace_selector_from_env_requires_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HOTDATA_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="HOTDATA_API_KEY"):
        workspace_selector_from_env()


def test_register_hotdata_sql_engine_is_idempotent() -> None:
    from marimo._sql.get_engines import SUPPORTED_ENGINES

    hm.unregister_hotdata_sql_engine()
    assert SUPPORTED_ENGINES.count(HotdataMarimoEngine) == 0
    try:
        hm.register_hotdata_sql_engine()
        hm.register_hotdata_sql_engine()
        assert SUPPORTED_ENGINES.count(HotdataMarimoEngine) == 1
    finally:
        hm.unregister_hotdata_sql_engine()


def test_hotdata_engine_display_name_in_marimo_ui(mock_client) -> None:
    hm.register_hotdata_sql_engine()
    try:
        engine = HotdataMarimoEngine(mock_client, engine_name=VariableName("client"))
        import marimo._sql.get_engines as ge
        import marimo._runtime.runner.hooks_post_execution as hpe

        for module in (ge, hpe):
            conn = module.engine_to_data_source_connection(VariableName("client"), engine)
            assert conn.display_name == "Hotdata"
    finally:
        hm.unregister_hotdata_sql_engine()
