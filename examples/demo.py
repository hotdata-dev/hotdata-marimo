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
    return browser, client, editor, history, recent, status


@app.cell
def _(mo):
    mo.md(r"""
    ## HotData explorer
    Use the tabs below to switch between available workspaces, connection status, dataset browsing, and SQL queries.
    """)
    return


@app.cell
def _(browser, editor, history, mo, recent, status, workspace):
    mo.ui.tabs({
        "Workspaces": workspace,
        "Connections": status,
        "Datasets": browser,
        "SQL query": editor,
        "Recent results": recent,
        "Run history": history,
    })
    return


@app.cell
def _(editor):
    # Explicitly touch nested widget values so Marimo reruns this cell on clicks.
    _run = editor.run.value
    _rerun = editor.rerun.value
    _clear = editor.clear.value
    return


@app.cell
def _(recent):
    _selected = recent.pick.value
    return


@app.cell
def _(client, mo):
    _df = mo.sql(
        f"""
        SELECT 1 AS example_value
        """,
        engine=client
    )
    return


if __name__ == "__main__":
    app.run()
