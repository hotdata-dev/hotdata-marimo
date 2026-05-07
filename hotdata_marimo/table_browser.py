from __future__ import annotations

from typing import Any

import marimo as mo

from hotdata_marimo.client import HotdataClient
from hotdata_marimo.connection_picker import connection_picker


class TableBrowser:
    """Pick a fully qualified `connection.schema.table` and inspect columns."""

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

        self.search = mo.ui.text(value="", label="Search", full_width=True)
        self._bootstrap_table_pick()

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

    def _bootstrap_table_pick(self) -> None:
        names = self._names_for_active_connection()
        self._all_names = names
        if not names:
            self.table_pick = mo.ui.dropdown(
                options={"(no tables in catalog)": ""},
                label="Table",
            )
            self._empty_catalog = True
        else:
            self._empty_catalog = False
            self.table_pick = mo.ui.dropdown(
                options={n: n for n in names},
                label="Table",
                full_width=True,
            )

    @property
    def selected_connection_id(self) -> str | None:
        return self._active_connection_id()

    @property
    def selected_table(self) -> str | None:
        v = self.table_pick.value
        return v if v else None

    @property
    def ui(self):
        _ = self.search.value
        if self._conn_pick is not None:
            _ = self._conn_pick.value

        self._all_names = self._names_for_active_connection()
        needle = self.search.value.strip().lower()
        if self._all_names:
            self._empty_catalog = False
            options = (
                [n for n in self._all_names if needle in n.lower()]
                if needle
                else self._all_names
            )
            if not options:
                options = self._all_names
            self.table_pick = mo.ui.dropdown(
                options={n: n for n in options},
                label="Table",
                full_width=True,
            )
        else:
            self._empty_catalog = True
            self.table_pick = mo.ui.dropdown(
                options={"(no tables in catalog)": ""},
                label="Table",
            )

        _ = self.table_pick.value
        sel = self.selected_table
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
                else "Choose a table below."
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
            stack.extend([self.search, self.table_pick])
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
                self.search,
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
