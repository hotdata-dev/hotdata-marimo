from __future__ import annotations

from typing import Any

import marimo as mo

from hotdata_runtime.client import HotdataClient


def connection_picker(
    client: HotdataClient,
    *,
    label: str = "Connection",
    full_width: bool = True,
):
    listing = client.connections().list_connections()
    conns = listing.connections
    if not conns:
        return mo.ui.dropdown(
            options={"(no connections)": ""},
            label=label,
            full_width=full_width,
        )
    options = {c.name: c.id for c in conns}
    return mo.ui.dropdown(
        options=options,
        label=label,
        full_width=full_width,
    )


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
            listing = client.connections().list_connections()
            conns = listing.connections
            if len(conns) > 1:
                self._conn_pick = connection_picker(client)
            elif len(conns) == 1:
                self._implicit_connection_id = conns[0].id
            else:
                self._implicit_connection_id = ""

        self._table_pick_ctx: str | None = None

        if self._conn_pick is not None:
            self.table_pick = mo.ui.dropdown(
                options={"(select connection above)": ""},
                label="Table",
                full_width=True,
            )
            self._empty_catalog = True
            self._all_names: list[str] = []
        else:
            names = self._names_for_active_connection()
            self._all_names = names
            if not names:
                self.table_pick = mo.ui.dropdown(
                    options={"(no tables in catalog)": ""},
                    label="Table",
                    full_width=True,
                )
                self._empty_catalog = True
            else:
                self._empty_catalog = False
                self.table_pick = mo.ui.dropdown(
                    options={n: n for n in names},
                    label="Table",
                    full_width=True,
                    searchable=True,
                )
            self._table_pick_ctx = self._active_connection_id()

    def _active_connection_id(self) -> str | None:
        if self._override_connection_id is not None:
            return self._override_connection_id or None
        if self._conn_pick is not None:
            v = self._conn_pick.value  # type: ignore[attr-defined]
            return v if v else None
        if self._implicit_connection_id is None:
            return None
        return self._implicit_connection_id or None

    def _names_for_active_connection(self) -> list[str]:
        cid = self._active_connection_id()
        if cid is None or cid == "":
            return []
        return self._client.list_qualified_table_names(
            limit=self._table_limit,
            connection_id=cid,
        )

    def _rebuild_table_pick(self, names: list[str]) -> None:
        self._all_names = names
        if not names:
            self._empty_catalog = True
            self.table_pick = mo.ui.dropdown(
                options={"(no tables in catalog)": ""},
                label="Table",
                full_width=True,
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
        self._rebuilt_table_pick_this_run = True

    @property
    def selected_connection_id(self) -> str | None:
        return self._active_connection_id()

    @property
    def selected_table(self) -> str | None:
        v = self.table_pick.value
        return v if v else None

    @property
    def ui(self):
        self._rebuilt_table_pick_this_run = False

        if self._conn_pick is not None:
            _ = self._conn_pick.value

        cid = self._active_connection_id()
        names = self._names_for_active_connection()

        if cid and cid != self._table_pick_ctx:
            self._rebuild_table_pick(names)

        if not self._rebuilt_table_pick_this_run:
            _ = self.table_pick.value

        sel = None if self._rebuilt_table_pick_this_run else self.selected_table
        conn_header = (
            mo.md(f"**Connection** `{self._active_connection_id()}`")
            if self._active_connection_id()
            else None
        )
        if not sel:
            hint = (
                "_No tables returned from the information schema. "
                "Try refreshing a connection in Hotdata._"
                if self._empty_catalog
                else "Choose a table below (search inside the dropdown when needed)."
            )
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

        cols = self._client.columns_for_qualified(sel)
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
