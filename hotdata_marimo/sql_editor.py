from __future__ import annotations

import marimo as mo

from hotdata_runtime import HotdataClient, QueryResult


class SqlEditor:
    """SQL workspace: textarea plus Run, with `result` after the button is pressed.

    Marimo does not allow reading ``.value`` on UI elements in the same cell that
    constructs them. Instantiate ``SqlEditor`` in one cell and use ``.ui`` / read
    ``.result`` in other cells (see the package README two-cell pattern).
    """

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
        self.rerun = mo.ui.button(
            value=0,
            on_click=lambda n: n + 1,
            label="Rerun last",
        )
        self.clear = mo.ui.button(
            value=0,
            on_click=lambda n: n + 1,
            label="Clear result",
            kind="neutral",
        )
        self._result_cache: QueryResult | None = None
        self._cached_sql: str | None = None
        self._last_run_n: int | None = None
        self._last_rerun_n: int | None = None
        self._last_clear_n: int | None = None
        self.show_history = mo.ui.checkbox(value=False, label="Show run history")

    @property
    def ui(self):
        _ = self.run.value
        _ = self.rerun.value
        _ = self.clear.value
        _ = self.show_history.value
        return mo.vstack(
            [
                self.sql,
                mo.md(
                    f"_Run clicks: {self.run.value} · "
                    f"Rerun clicks: {self.rerun.value} · "
                    f"Clear clicks: {self.clear.value}_"
                ),
                mo.hstack(
                    [
                        self.run,
                        self.rerun,
                        self.clear,
                        self.show_history,
                    ],
                    gap=1,
                ),
                (
                    mo.accordion(
                        {
                            "Run history": mo.lazy(
                                lambda: __import__(
                                    "hotdata_marimo.display",
                                    fromlist=["run_history"],
                                ).run_history(self._client)
                            )
                        }
                    )
                    if self.show_history.value
                    else mo.md("")
                ),
            ],
            gap=1,
        )

    def _apply_clear(self, clear_n: int) -> bool:
        if clear_n > 0 and self._last_clear_n != clear_n:
            self._result_cache = None
            self._cached_sql = None
            self._last_clear_n = clear_n
            return True
        return False

    def _execute_or_cached(self) -> QueryResult | None:
        sql_text = self.sql.value
        run_n = self.run.value
        rerun_n = self.rerun.value

        if rerun_n > 0 and rerun_n != self._last_rerun_n:
            if self._cached_sql is None:
                return None
            with mo.status.spinner(
                title="Running on Hotdata",
                subtitle="Re-running last query and waiting for results…",
            ):
                result = self._client.execute_sql(self._cached_sql or "")
            self._result_cache = result
            self._last_rerun_n = rerun_n
            return result

        if run_n > 0 and run_n != self._last_run_n:
            with mo.status.spinner(
                title="Running on Hotdata",
                subtitle="Executing query and waiting for results…",
            ):
                result = self._client.execute_sql(sql_text)
            self._result_cache = result
            self._cached_sql = sql_text
            self._last_run_n = run_n
            return result

        if self._result_cache is not None and sql_text == self._cached_sql:
            return self._result_cache

        return None

    @property
    def result_panel(self):
        from hotdata_marimo.display import query_result

        run_n = self.run.value
        rerun_n = self.rerun.value
        clear_n = self.clear.value

        if self._apply_clear(clear_n):
            return mo.md("Result cleared. Click **Run on Hotdata** to execute again.")

        if run_n == 0 and rerun_n == 0 and self._result_cache is None:
            return mo.md("_Click **Run on Hotdata** to execute._")

        if rerun_n > 0 and rerun_n != self._last_rerun_n and self._cached_sql is None:
            return mo.md("No previous SQL to rerun yet — click **Run on Hotdata** first.")

        result = self._execute_or_cached()
        if result is not None:
            return query_result(result)

        return mo.md("SQL changed — click **Run on Hotdata** again to execute.")

    @property
    def tab_ui(self):
        _ = self.run.value
        _ = self.rerun.value
        _ = self.clear.value
        _ = self.show_history.value
        return mo.vstack([self.ui, self.result_panel], gap=2)

    @property
    def result(self) -> QueryResult:
        run_n = self.run.value
        rerun_n = self.rerun.value
        clear_n = self.clear.value

        if self._apply_clear(clear_n):
            mo.stop(True, mo.md("Result cleared. Click **Run on Hotdata** to execute again."))

        mo.stop(
            run_n == 0 and rerun_n == 0,
            mo.md(
                "**Run on Hotdata** is on the SQL editor UI (a cell that **returns** "
                "`editor.ui` or `mo.vstack([browser.ui, editor.ui])`). Click it there, "
                "then this cell will run."
            ),
        )

        if rerun_n > 0 and rerun_n != self._last_rerun_n:
            mo.stop(
                self._cached_sql is None,
                mo.md("No previous SQL to rerun yet — click **Run on Hotdata** first."),
            )

        result = self._execute_or_cached()
        if result is not None:
            return result

        mo.stop(
            True,
            mo.md("SQL changed — click **Run on Hotdata** again to execute."),
        )


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
