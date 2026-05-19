"""Marimo UI for managed Hotdata databases (create + parquet table loads)."""

from __future__ import annotations

import os
import tempfile

import marimo as mo

from hotdata_runtime import (
    DEFAULT_SCHEMA,
    HotdataClient,
    LoadManagedTableResult,
    ManagedDatabase,
)

from hotdata_marimo._options import empty_dropdown


def _parse_table_names(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _upload_parquet_bytes(client: HotdataClient, contents: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        tmp.write(contents)
        path = tmp.name
    try:
        return client.upload_parquet(path)
    finally:
        os.unlink(path)


def databases_panel(client: HotdataClient):
    """Table of managed databases in the workspace."""
    dbs = client.list_managed_databases()
    if not dbs:
        return mo.vstack(
            [
                mo.md("### Managed databases"),
                mo.md("_No managed databases yet._"),
                mo.md(
                    "Create one below, or with the CLI: "
                    "`hotdata databases create --name <name> --table <table>`."
                ),
            ],
            gap=1,
        )
    rows: list[dict[str, object]] = [
        {"name": db.name, "id": db.id, "sql_prefix": f"{db.name}.{{schema}}.{{table}}"}
        for db in dbs
    ]
    return mo.vstack(
        [
            mo.md("### Managed databases"),
            mo.ui.table(
                rows,
                label="Managed databases",
                pagination=True,
                page_size=min(10, len(rows)),
                selection=None,
                max_height=240,
            ),
            mo.md("_Query as `database.schema.table` in SQL._"),
        ],
        gap=1,
    )


class ManagedDatabaseWriter:
    """Create managed databases and load parquet files into declared tables.

    Instantiate in one cell and use ``.tab_ui`` in another (see package README).
    """

    def __init__(
        self,
        client: HotdataClient,
        *,
        default_schema: str = DEFAULT_SCHEMA,
    ) -> None:
        self._client = client
        self._default_schema = default_schema
        self._last_create_n: int | None = None
        self._last_load_n: int | None = None
        self._create_result: ManagedDatabase | None = None
        self._load_result: LoadManagedTableResult | None = None
        self._create_error: str | None = None
        self._load_error: str | None = None
        self._show_create_success = False
        self._show_load_success = False

        self.name = mo.ui.text("", label="Database name", full_width=True)
        self.schema = mo.ui.text(default_schema, label="Schema", full_width=True)
        self.tables = mo.ui.text_area(
            "",
            label="Tables to declare (one per line)",
            full_width=True,
        )
        self.create = mo.ui.button(
            value=0,
            on_click=lambda n: n + 1,
            label="Create database",
            kind="success",
        )

        self._rebuild_database_pick()
        self.table = mo.ui.text("", label="Table name", full_width=True)
        self.file = mo.ui.file(
            filetypes=[".parquet"],
            label="Parquet file",
            kind="area",
        )
        self.load = mo.ui.button(
            value=0,
            on_click=lambda n: n + 1,
            label="Load table",
            kind="success",
        )

    def _rebuild_database_pick(self) -> None:
        current = getattr(getattr(self, "database", None), "value", None)
        dbs = self._client.list_managed_databases()
        if not dbs:
            self.database = empty_dropdown(
                label="Database",
                message="(create one first)",
            )
            return
        options = {db.name: db.name for db in dbs}
        value = current if current in options else next(iter(options))
        self.database = mo.ui.dropdown(
            options=options,
            label="Database",
            full_width=True,
            value=value,
        )

    def _maybe_create(self) -> None:
        create_n = self.create.value
        if create_n == 0 or create_n == self._last_create_n:
            return
        self._last_create_n = create_n
        self._create_error = None
        self._create_result = None
        self._show_create_success = False
        self._show_load_success = False
        db_name = self.name.value.strip()
        if not db_name:
            self._create_error = "Enter a database name."
            return
        schema = self.schema.value.strip() or self._default_schema
        tables = _parse_table_names(self.tables.value)
        try:
            self._create_result = self._client.create_managed_database(
                db_name,
                schema=schema,
                tables=tables or None,
            )
            self._rebuild_database_pick()
            self._show_create_success = True
        except (RuntimeError, ValueError, KeyError) as e:
            self._create_error = str(e)

    def _maybe_load(self) -> None:
        load_n = self.load.value
        if load_n == 0 or load_n == self._last_load_n:
            return
        self._last_load_n = load_n
        self._load_error = None
        self._load_result = None
        self._show_load_success = False
        database = self.database.value
        table = self.table.value.strip()
        if not database:
            self._load_error = "Choose or create a database first."
            return
        if not table:
            self._load_error = "Enter a table name."
            return
        uploads = self.file.value
        if not uploads:
            self._load_error = "Choose a parquet file to upload."
            return
        schema = self.schema.value.strip() or self._default_schema
        try:
            upload_id = _upload_parquet_bytes(self._client, uploads[0].contents)
            self._load_result = self._client.load_managed_table(
                database,
                table,
                schema=schema,
                upload_id=upload_id,
            )
            self._show_load_success = True
            self._show_create_success = False
        except (RuntimeError, ValueError, KeyError, OSError) as e:
            self._load_error = str(e)

    @property
    def result_panel(self):
        _ = self.create.value
        _ = self.load.value
        self._maybe_create()
        self._maybe_load()

        if self._create_error:
            return mo.callout(mo.md(self._create_error), kind="danger")
        if self._show_create_success and self._create_result is not None:
            db = self._create_result
            return mo.callout(
                mo.md(
                    f"Created **{db.name}** (`{db.id}`). "
                    "Load parquet into a declared table below."
                ),
                kind="success",
            )

        if self._load_error:
            return mo.callout(mo.md(self._load_error), kind="danger")
        if self._show_load_success and self._load_result is not None:
            loaded = self._load_result
            return mo.callout(
                mo.md(
                    f"Loaded **{loaded.full_name}** · **{loaded.row_count}** rows."
                ),
                kind="success",
            )

        return mo.md("_Create a database or load a parquet table to see results here._")

    @property
    def ui(self):
        _ = self.create.value
        _ = self.load.value
        _ = self.database.value
        return mo.vstack(
            [
                mo.md("### Create database"),
                self.name,
                self.schema,
                self.tables,
                self.create,
                mo.md("### Load parquet table"),
                self.database,
                self.table,
                self.file,
                self.load,
            ],
            gap=1,
        )

    @property
    def tab_ui(self):
        _ = self.create.value
        _ = self.load.value
        if hasattr(self.database, "value"):
            _ = self.database.value
        return mo.vstack(
            [
                databases_panel(self._client),
                self.ui,
                self.result_panel,
            ],
            gap=2,
        )


def managed_database_writer(
    client: HotdataClient,
    *,
    default_schema: str = DEFAULT_SCHEMA,
) -> ManagedDatabaseWriter:
    return ManagedDatabaseWriter(client, default_schema=default_schema)
