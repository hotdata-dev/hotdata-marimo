"""Marimo-native UI and helpers for Hotdata."""

from hotdata_marimo.client import HotdataClient, from_env
from hotdata_marimo.connection_picker import connection_picker
from hotdata_marimo.query_result import query_result
from hotdata_marimo.recent_results import RecentResults, recent_results
from hotdata_marimo.result import QueryResult
from hotdata_marimo.sql_editor import SqlEditor, sql_editor
from hotdata_marimo.status import connection_status
from hotdata_marimo.table_browser import TableBrowser, table_browser
from hotdata_marimo.workspace_selector import WorkspaceSelector, workspace_selector_from_env

__all__ = [
    "HotdataClient",
    "QueryResult",
    "RecentResults",
    "SqlEditor",
    "TableBrowser",
    "connection_picker",
    "connection_status",
    "from_env",
    "hotdata_connection_picker",
    "hotdata_query_result",
    "hotdata_recent_results",
    "hotdata_sql_editor",
    "hotdata_table_browser",
    "hotdata_workspace_selector",
    "recent_results",
    "query_result",
    "sql_editor",
    "table_browser",
    "WorkspaceSelector",
    "workspace_selector_from_env",
    "register_mo_ui_hotdata_aliases",
]

hotdata_sql_editor = sql_editor
hotdata_table_browser = table_browser
hotdata_query_result = query_result
hotdata_connection_picker = connection_picker
hotdata_workspace_selector = workspace_selector_from_env
hotdata_recent_results = recent_results


def register_mo_ui_hotdata_aliases() -> None:
    """Attach Hotdata helpers to ``marimo.ui`` for discoverability (``mo.ui.hotdata_*``)."""
    import marimo as mo

    mo.ui.hotdata_sql_editor = hotdata_sql_editor  # type: ignore[attr-defined]
    mo.ui.hotdata_table_browser = hotdata_table_browser  # type: ignore[attr-defined]
    mo.ui.hotdata_query_result = hotdata_query_result  # type: ignore[attr-defined]
    mo.ui.hotdata_connection_status = connection_status  # type: ignore[attr-defined]
    mo.ui.hotdata_connection_picker = hotdata_connection_picker  # type: ignore[attr-defined]
    mo.ui.hotdata_workspace_selector = hotdata_workspace_selector  # type: ignore[attr-defined]
    mo.ui.hotdata_recent_results = hotdata_recent_results  # type: ignore[attr-defined]


register_mo_ui_hotdata_aliases()
