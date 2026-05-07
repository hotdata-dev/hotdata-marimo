import marimo

__generated_with = "0.23.5"
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
        not os.environ.get("HOTDATA_API_KEY"),
        mo.callout(
            mo.md(
                "Add **HOTDATA_API_KEY** to your environment to run this example."
            ),
            kind="warn",
        ),
    )
    client = hm.from_env()
    return (client,)


@app.cell
def _(client, hm, mo):
    browser = hm.table_browser(client)
    editor = hm.sql_editor(client, default_sql="SELECT 1 AS ok")
    mo.vstack([browser.ui, editor.ui], gap=2)
    return (editor,)


@app.cell
def _(editor, hm):
    result = editor.result
    hm.query_result(result)
    return


if __name__ == "__main__":
    app.run()
