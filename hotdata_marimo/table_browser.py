from __future__ import annotations

from typing import Any

import marimo as mo

from hotdata_runtime import HotdataClient

from hotdata_marimo._options import (
    connection_picker,
    empty_dropdown,
    resolve_connection_picker,
)

__all__ = ["TableBrowser", "connection_picker", "table_browser"]


class TableBrowser:
    """Pick a fully qualified `connection.schema.table` and inspect columns.

    Marimo does not allow reading ``.value`` on UI elements in the same cell that
    constructs them. Build ``TableBrowser`` in one cell and use ``.ui`` in another.

    The table dropdown is not recreated on every render (that would make it
    "born" in the layout cell). It is only rebuilt when the active connection
    changes: after a rebuild, ``.value`` is not read until a later run.
    """

    def __init__(
        self,
        client: HotdataClient,
        *,
        table_limit: int = 5000,
        connection_id: str | None = None,
    ) -> None:
        self._client = client
        self._table_limit = table_limit
        self._override_connection_id = connection_id
        self._conn_pick: Any | None = None
        self._implicit_connection_id: str | None = None

        if self._override_connection_id is None:
            self._conn_pick, self._implicit_connection_id = resolve_connection_picker(
                client
            )

        self._table_pick_ctx: str | None = None
        self._init_table_pick()

    def _active_connection_id(self) -> str | None:
        if self._override_connection_id is not None:
            return self._override_connection_id or None
        if self._conn_pick is not None:
            return self._conn_pick.value or None  # type: ignore[attr-defined]
        return self._implicit_connection_id or None

    def _names_for_active_connection(self) -> list[str]:
        cid = self._active_connection_id()
        if not cid:
            return []
        return self._client.list_qualified_table_names(
            limit=self._table_limit,
            connection_id=cid,
        )

    def _set_table_pick(self, names: list[str]) -> None:
        """Create or replace the table dropdown for the given names list."""
        self._all_names = names
        if not names:
            self._empty_catalog = True
            self.table_pick = empty_dropdown(
                label="Table",
                message="(no tables in catalog)",
            )
        else:
            self._empty_catalog = False
            self.table_pick = mo.ui.dropdown(
                options={n: n for n in names},
                label="Table",
                full_width=True,
                searchable=True,
            )
        self._table_pick_ctx = self._active_connection_id()

    def _init_table_pick(self) -> None:
        if self._conn_pick is not None:
            self._all_names = []
            self._empty_catalog = True
            self.table_pick = empty_dropdown(
                label="Table",
                message="(select connection above)",
            )
            self._table_pick_ctx = ""
            return
        self._set_table_pick(self._names_for_active_connection())

    def _sync_table_catalog(self) -> bool:
        """Refresh the table dropdown when the active connection changes.

        Returns True if the dropdown was rebuilt (so the caller knows not to
        read ``.value`` on the new widget in the same Marimo run).
        """
        if self._conn_pick is not None:
            _ = self._conn_pick.value  # type: ignore[attr-defined]
        cid = self._active_connection_id()
        if not cid or cid == self._table_pick_ctx:
            return False
        self._set_table_pick(self._names_for_active_connection())
        return True

    @property
    def selected_connection_id(self) -> str | None:
        return self._active_connection_id()

    @property
    def selected_table(self) -> str | None:
        v = self.table_pick.value
        return v if v else None

    @property
    def ui(self):
        rebuilt = self._sync_table_catalog()
        if not rebuilt:
            _ = self.table_pick.value

        sel = None if rebuilt else self.selected_table
        cid = self._active_connection_id()
        conn_header = (
            mo.md(f"**Connection** `{cid}`")
            if cid
            else None
        )
        if not sel:
            if self._conn_pick is not None and not cid:
                hint = "Choose a connection above to load tables."
            elif self._empty_catalog:
                hint = (
                    "_No tables returned from the information schema. "
                    "Try refreshing a connection in Hotdata._"
                )
            else:
                hint = "Choose a table below (search inside the dropdown when needed)."
            stack = [
                mo.md(
                    f"**Workspace** `{self._client.workspace_id}` — {hint}"
                ),
            ]
            if conn_header is not None:
                stack.append(conn_header)
            if self._conn_pick is not None:
                stack.append(self._conn_pick)
            stack.append(self.table_pick)
            return mo.vstack(stack, gap=1)

        cols = self._client.columns_for_qualified(
            sel,
            connection_id=self.selected_connection_id,
        )
        if not cols:
            body = mo.md("_No column metadata returned (check catalog sync)._")
        else:
            lines = [
                f"| `{c.name}` | {c.data_type} | "
                f"{'NULL' if c.nullable else 'NOT NULL'} |"
                for c in cols
            ]
            table = (
                "| column | type | null |\n| --- | --- | --- |\n"
                + "\n".join(lines)
            )
            body = mo.md(table)
        starter = f"```sql\nSELECT *\nFROM {sel}\nLIMIT 100\n```"
        stack2 = [
            mo.md(
                f"**Workspace** `{self._client.workspace_id}` — "
                f"**selected** `{sel}`"
            ),
        ]
        if conn_header is not None:
            stack2.append(conn_header)
        if self._conn_pick is not None:
            stack2.append(self._conn_pick)
        stack2.extend(
            [
                self.table_pick,
                mo.md("### Columns"),
                body,
                mo.md("### Starter query"),
                mo.md(starter),
            ]
        )
        return mo.vstack(stack2, gap=1)


def table_browser(
    client: HotdataClient,
    *,
    table_limit: int = 5000,
    connection_id: str | None = None,
) -> TableBrowser:
    return TableBrowser(
        client, table_limit=table_limit, connection_id=connection_id
    )
