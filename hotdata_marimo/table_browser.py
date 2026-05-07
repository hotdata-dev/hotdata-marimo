from __future__ import annotations

import marimo as mo

from hotdata_marimo.client import HotdataClient


class TableBrowser:
    """Pick a fully qualified `connection.schema.table` and inspect columns."""

    def __init__(self, client: HotdataClient, *, table_limit: int = 5000) -> None:
        self._client = client
        self._all_names = client.list_qualified_table_names(limit=table_limit)
        self.search = mo.ui.text(value="", label="Search", full_width=True)
        names = self._all_names
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
    def selected_table(self) -> str | None:
        v = self.table_pick.value
        return v if v else None

    @property
    def ui(self):
        _ = self.search.value
        needle = self.search.value.strip().lower()
        if not self._empty_catalog:
            options = (
                [n for n in self._all_names if needle in n.lower()]
                if needle
                else self._all_names
            )
            self.table_pick = mo.ui.dropdown(
                options={n: n for n in options},
                label="Table",
                full_width=True,
            )
        _ = self.table_pick.value
        sel = self.selected_table
        if not sel:
            hint = (
                "_No tables returned from the information schema. "
                "Try refreshing a connection in Hotdata._"
                if self._empty_catalog
                else "Choose a table below."
            )
            return mo.vstack(
                [
                    mo.md(
                        f"**Workspace** `{self._client.workspace_id}` — {hint}"
                    ),
                    self.search,
                    self.table_pick,
                ],
                gap=1,
            )
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
        return mo.vstack(
            [
                mo.md(
                    f"**Workspace** `{self._client.workspace_id}` — "
                    f"**selected** `{sel}`"
                ),
                self.search,
                self.table_pick,
                mo.md("### Columns"),
                body,
                mo.md("### Starter query"),
                mo.md(starter),
            ],
            gap=1,
        )


def table_browser(client: HotdataClient, *, table_limit: int = 5000) -> TableBrowser:
    return TableBrowser(client, table_limit=table_limit)
