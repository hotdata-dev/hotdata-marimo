"""Marimo-native UI and helpers for Hotdata (built on hotdata-runtime)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hotdata-marimo")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

from hotdata_runtime import HotdataClient, QueryResult, from_env

from hotdata_marimo.databases import (
    ManagedDatabaseWriter,
    databases_panel,
    managed_database_writer,
)
from hotdata_marimo.display import (
    RecentResults,
    connection_status,
    connections_panel,
    query_result,
    recent_results,
    run_history,
)
from hotdata_marimo.sql_editor import SqlEditor, sql_editor
from hotdata_marimo.sql_engine import (
    HotdataMarimoEngine,
    register_hotdata_sql_engine,
    unregister_hotdata_sql_engine,
)
from hotdata_marimo.table_browser import TableBrowser, connection_picker, table_browser
from hotdata_marimo.workspace_selector import WorkspaceSelector, workspace_selector_from_env

__all__ = [
    "HotdataClient",
    "HotdataMarimoEngine",
    "ManagedDatabaseWriter",
    "QueryResult",
    "RecentResults",
    "SqlEditor",
    "TableBrowser",
    "WorkspaceSelector",
    "__version__",
    "connection_picker",
    "connection_status",
    "connections_panel",
    "databases_panel",
    "from_env",
    "hotdata_connection_picker",
    "hotdata_databases_panel",
    "hotdata_managed_database_writer",
    "hotdata_query_result",
    "hotdata_recent_results",
    "hotdata_sql_editor",
    "hotdata_table_browser",
    "hotdata_workspace_selector",
    "managed_database_writer",
    "query_result",
    "recent_results",
    "register_hotdata_sql_engine",
    "register_mo_ui_hotdata_aliases",
    "run_history",
    "sql_editor",
    "table_browser",
    "unregister_hotdata_sql_engine",
    "workspace_selector_from_env",
]

hotdata_sql_editor = sql_editor
hotdata_table_browser = table_browser
hotdata_query_result = query_result
hotdata_connection_picker = connection_picker
hotdata_databases_panel = databases_panel
hotdata_managed_database_writer = managed_database_writer
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
    mo.ui.hotdata_databases_panel = hotdata_databases_panel  # type: ignore[attr-defined]
    mo.ui.hotdata_managed_database_writer = hotdata_managed_database_writer  # type: ignore[attr-defined]
    mo.ui.hotdata_workspace_selector = hotdata_workspace_selector  # type: ignore[attr-defined]
    mo.ui.hotdata_recent_results = hotdata_recent_results  # type: ignore[attr-defined]


register_mo_ui_hotdata_aliases()
