from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from hotdata_runtime import LoadManagedTableResult, ManagedDatabase

from hotdata_marimo.databases import ManagedDatabaseWriter, databases_panel


def test_databases_panel_empty_state(mock_client):
    mock_client.list_managed_databases.return_value = []
    with patch("hotdata_marimo.databases.mo.md", side_effect=lambda x: x):
        panel = databases_panel(mock_client)
    assert panel is not None


def test_databases_panel_lists_managed_databases(mock_client):
    mock_client.list_managed_databases.return_value = [
        ManagedDatabase(id="c1", description="sales", default_connection_id="conn_c1"),
    ]
    with patch("hotdata_marimo.databases.mo.vstack", return_value="panel"), patch(
        "hotdata_marimo.databases.mo.md", side_effect=lambda x: x
    ), patch("hotdata_marimo.databases.mo.ui.table", return_value=MagicMock()):
        panel = databases_panel(mock_client)
    assert panel == "panel"


def test_managed_database_writer_creates_database(mock_client):
    mock_client.list_managed_databases.return_value = []
    mock_client.create_managed_database.return_value = ManagedDatabase(
        id="conn_new",
        description="sales",
        default_connection_id="conn_c1",
    )
    create = MagicMock()
    create.value = 1
    name = MagicMock()
    name.value = "sales"
    schema = MagicMock()
    schema.value = "public"
    tables = MagicMock()
    tables.value = "orders\ncustomers"
    load = MagicMock()
    load.value = 0
    database = MagicMock()
    database.value = ""
    table = MagicMock()
    table.value = ""
    file = MagicMock()
    file.value = []

    with patch("hotdata_marimo.databases.mo.ui.button", side_effect=[create, load]), patch(
        "hotdata_marimo.databases.mo.ui.text", side_effect=[name, schema, table]
    ), patch(
        "hotdata_marimo.databases.mo.ui.text_area", return_value=tables
    ), patch(
        "hotdata_marimo.databases.empty_dropdown", return_value=database
    ), patch(
        "hotdata_marimo.databases.mo.ui.dropdown", return_value=database
    ), patch(
        "hotdata_marimo.databases.mo.ui.file", return_value=file
    ), patch(
        "hotdata_marimo.databases.databases_panel", return_value="list"
    ), patch(
        "hotdata_marimo.databases.mo.md", side_effect=lambda x: x
    ), patch(
        "hotdata_marimo.databases.mo.callout", side_effect=lambda body, **kw: body
    ):
        writer = ManagedDatabaseWriter(mock_client)
        panel = writer.result_panel

    mock_client.create_managed_database.assert_called_once_with(
        description="sales",
        schema="public",
        tables=["orders", "customers"],
    )
    assert "Created" in str(panel)


def test_managed_database_writer_loads_parquet(mock_client):
    mock_client.list_managed_databases.return_value = [
        ManagedDatabase(id="c1", description="sales", default_connection_id="conn_c1"),
    ]
    mock_client.upload_parquet.return_value = "upl_1"
    mock_client.load_managed_table.return_value = LoadManagedTableResult(
        connection_id="c1",
        schema_name="public",
        table_name="orders",
        row_count=10,
        full_name="sales.public.orders",
    )

    create = MagicMock()
    create.value = 0
    load = MagicMock()
    load.value = 1
    name = MagicMock()
    name.value = ""
    schema = MagicMock()
    schema.value = "public"
    tables = MagicMock()
    tables.value = ""
    database = MagicMock()
    database.value = "sales"
    table = MagicMock()
    table.value = "orders"
    file = MagicMock()
    file.value = [SimpleNamespace(name="orders.parquet", contents=b"PAR1")]

    with patch("hotdata_marimo.databases.mo.ui.button", side_effect=[create, load]), patch(
        "hotdata_marimo.databases.mo.ui.text", side_effect=[name, schema, table]
    ), patch(
        "hotdata_marimo.databases.mo.ui.text_area", return_value=tables
    ), patch(
        "hotdata_marimo.databases.mo.ui.dropdown", return_value=database
    ), patch(
        "hotdata_marimo.databases.mo.ui.file", return_value=file
    ), patch(
        "hotdata_marimo.databases.databases_panel", return_value="list"
    ), patch(
        "hotdata_marimo.databases._upload_parquet_bytes", return_value="upl_1"
    ):
        writer = ManagedDatabaseWriter(mock_client)
        panel = writer.result_panel

    mock_client.load_managed_table.assert_called_once_with(
        "sales",
        "orders",
        schema="public",
        upload_id="upl_1",
    )
    assert panel is not None
