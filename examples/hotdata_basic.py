import marimo

__generated_with = "0.23.5"
# Local dev (no /auth/login): marimo edit examples/hotdata_basic.py --no-token
app = marimo.App()


@app.cell
def _():
    import os

    import marimo as mo

    import hotdata_marimo as hm

    return hm, mo, os


@app.cell
def _(hm, mo, os):
    mo.stop(
        not (
            os.environ.get("HOTDATA_API_KEY")
            or os.environ.get("HOTDATA_TOKEN")
        ),
        mo.callout(
            mo.md(
                "Add **HOTDATA_API_KEY** (or **HOTDATA_TOKEN**) to your environment "
                "to run this example."
            ),
            kind="warn",
        ),
    )
    client = hm.from_env()
    return (client,)


@app.cell
def _(client, hm, mo):
    id_map = client.connection_id_by_name()
    tpch_id = id_map.get("tpch")
    mo.stop(
        not tpch_id,
        mo.callout(
            mo.md(
                "This example expects a connection named **tpch**. "
                "Create it in Hotdata or adjust the name in the notebook."
            ),
            kind="warn",
        ),
    )
    browser = hm.table_browser(client, connection_id=tpch_id)
    editor = hm.sql_editor(
        client,
        default_sql="SELECT * FROM tpch.tpch_sf1.nation LIMIT 5",
    )
    return browser, editor


@app.cell
def _(browser, editor, hm, mo):
    return mo.vstack(
        [
            browser.ui,
            editor.ui,
            mo.lazy(lambda: hm.query_result(editor.result)),
        ],
        gap=2,
    )


if __name__ == "__main__":
    app.run()
