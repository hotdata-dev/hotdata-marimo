import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def _():
    import os

    import marimo as mo

    import hotdata_marimo as hm

    hm.register_hotdata_sql_engine()
    return hm, mo, os


@app.cell
def _(hm, mo, os):
    mo.stop(
        not os.environ.get("HOTDATA_API_KEY"),
        mo.callout(
            mo.md(
                "Add **HOTDATA_API_KEY** to your environment "
                "to run this example."
            ),
            kind="warn",
        ),
    )
    workspace = hm.workspace_selector_from_env()
    return (workspace,)


@app.cell
def _(hm, workspace):
    client = workspace.client
    status = hm.connection_status(client)
    browser = hm.table_browser(client)
    editor = hm.sql_editor(
        client,
        default_sql="SELECT 1 AS ok",
    )
    recent = hm.recent_results(client, limit=20)
    history = hm.run_history(client, limit=10)
    return browser, client, editor, history, recent, status, workspace


@app.cell
def _(browser, editor, mo, recent, status, workspace):
    return mo.vstack(
        [
            workspace.ui,
            status,
            browser.ui,
            editor.ui,
            recent.ui,
        ],
        gap=2,
    )


@app.cell
def _(history):
    return history


@app.cell
def _(editor, hm):
    # Explicitly touch nested widget values so Marimo reruns this cell on clicks.
    _run = editor.run.value
    _rerun = editor.rerun.value
    _clear = editor.clear.value
    return hm.query_result(editor.result), _clear, _rerun, _run


@app.cell
def _(hm, recent):
    _selected = recent.pick.value
    return hm.query_result(recent.result, label="Recent result"), _selected


@app.cell
def _(client, mo):
    _df = mo.sql(
        """
        SELECT 1 AS example_value
        """,
        engine=client,
    )
    return


if __name__ == "__main__":
    app.run()
