"""Marimo-native UI and helpers for Hotdata."""

from hotdata_marimo.client import HotdataClient, from_env
from hotdata_marimo.query_result import query_result
from hotdata_marimo.result import QueryResult
from hotdata_marimo.sql_editor import SqlEditor, sql_editor
from hotdata_marimo.status import connection_status
from hotdata_marimo.table_browser import TableBrowser, table_browser

__all__ = [
    "HotdataClient",
    "QueryResult",
    "SqlEditor",
    "TableBrowser",
    "connection_status",
    "from_env",
    "hotdata_query_result",
    "hotdata_sql_editor",
    "hotdata_table_browser",
    "query_result",
    "sql_editor",
    "table_browser",
    "register_mo_ui_hotdata_aliases",
]

hotdata_sql_editor = sql_editor
hotdata_table_browser = table_browser
hotdata_query_result = query_result


def register_mo_ui_hotdata_aliases() -> None:
    """Attach Hotdata helpers to ``marimo.ui`` for discoverability (``mo.ui.hotdata_*``)."""
    import marimo as mo

    mo.ui.hotdata_sql_editor = hotdata_sql_editor  # type: ignore[attr-defined]
    mo.ui.hotdata_table_browser = hotdata_table_browser  # type: ignore[attr-defined]
    mo.ui.hotdata_query_result = hotdata_query_result  # type: ignore[attr-defined]
    mo.ui.hotdata_connection_status = connection_status  # type: ignore[attr-defined]


register_mo_ui_hotdata_aliases()
