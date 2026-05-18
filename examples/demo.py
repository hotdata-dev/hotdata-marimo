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
    status = hm.connections_panel(client)
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
def _(browser):
    # Register connection/table widget deps so Marimo reruns layout cells on change.
    if browser._conn_pick is not None:
        _ = browser._conn_pick.value
    _ = browser.table_pick.value
    return


@app.cell
def _(browser):
    browser_ui = browser.ui
    return (browser_ui,)


@app.cell
def _(editor):
    editor_ui = editor.ui
    return (editor_ui,)


@app.cell
def _(editor, hm):
    _run = editor.run.value
    _rerun = editor.rerun.value
    _clear = editor.clear.value
    sql_result = hm.query_result(editor.result)
    return (sql_result,)


@app.cell
def _(editor_ui, mo, sql_result):
    sql_tab = mo.vstack([editor_ui, sql_result], gap=2)
    return (sql_tab,)


@app.cell
def _(hm, recent):
    recent_result = hm.query_result(recent.result, label="Recent result")
    return (recent_result,)


@app.cell
def _(mo, recent, recent_result):
    recent_tab = mo.vstack([recent.ui, recent_result], gap=2)
    return (recent_tab,)


@app.cell
def _(browser_ui, history, mo, recent_tab, sql_tab, status, workspace):
    mo.ui.tabs({
        "Workspaces": workspace.ui,
        "Connections": status,
        "Datasets": browser_ui,
        "SQL query": sql_tab,
        "Recent results": recent_tab,
        "Run history": history,
    })
    return


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
