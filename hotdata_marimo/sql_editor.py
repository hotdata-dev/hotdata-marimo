from __future__ import annotations

import marimo as mo

from hotdata_marimo.client import HotdataClient
from hotdata_marimo.result import QueryResult


class SqlEditor:
    """SQL workspace: textarea plus Run, with `result` after the button is pressed."""

    def __init__(
        self,
        client: HotdataClient,
        *,
        default_sql: str = "",
        label: str = "SQL",
        run_label: str = "Run on Hotdata",
    ) -> None:
        self._client = client
        self.sql = mo.ui.text_area(default_sql, label=label)
        self.run = mo.ui.button(
            value=0,
            on_click=lambda n: n + 1,
            label=run_label,
            kind="success",
        )
        self._result_cache: QueryResult | None = None
        self._cached_n: int | None = None
        self._cached_sql: str | None = None

    @property
    def ui(self):
        _ = self.run.value
        return mo.vstack(
            [
                self.sql,
                self.run,
            ],
            gap=1,
        )

    @property
    def result(self) -> QueryResult:
        mo.stop(
            self.run.value == 0,
            mo.md("Click **Run on Hotdata** to execute the query."),
        )
        n = self.run.value
        sql_text = self.sql.value
        if (
            self._result_cache is not None
            and n == self._cached_n
            and sql_text == self._cached_sql
        ):
            return self._result_cache
        mo.stop(
            n == self._cached_n and sql_text != self._cached_sql,
            mo.md("SQL changed — click **Run on Hotdata** again to execute."),
        )
        with mo.status.spinner(
            title="Running on Hotdata",
            subtitle="Executing query and waiting for results…",
        ):
            result = self._client.execute_sql(sql_text)
        self._result_cache = result
        self._cached_n = n
        self._cached_sql = sql_text
        return result


def sql_editor(
    client: HotdataClient,
    *,
    default_sql: str = "",
    label: str = "SQL",
    run_label: str = "Run on Hotdata",
) -> SqlEditor:
    return SqlEditor(
        client, default_sql=default_sql, label=label, run_label=run_label
    )
