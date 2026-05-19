import marimo

__generated_with = "0.23.6"
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
    db_writer = hm.managed_database_writer(client)
    recent = hm.recent_results(client, limit=20)
    history = hm.run_history(client, limit=10)
    return client, db_writer, history, recent, status


@app.cell
def _(mo):
    mo.md(r"""
    ## HotData explorer
    Use the tabs below to switch between workspaces, connections, managed databases,
    recent results, and run history.

    On a shared or networked host, run Marimo **without** `--no-token` and open the printed URL
    with its access token so only you can use this notebook.
    """)
    return


@app.cell
def _(db_writer):
    databases_tab = db_writer.tab_ui
    return (databases_tab,)


@app.cell
def _(recent):
    recent_tab = recent.tab_ui
    return (recent_tab,)


@app.cell
def _(databases_tab, history, mo, recent_tab, status, workspace):
    mo.ui.tabs({
        "Workspaces": workspace.ui,
        "Connections": status,
        "Databases": databases_tab,
        "Recent results": recent_tab,
        "Run history": history,
    })
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
