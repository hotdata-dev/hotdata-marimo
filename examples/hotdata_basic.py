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
                "Add **HOTDATA_API_KEY** to your environment "
                "to run this example."
            ),
            kind="warn",
        ),
    )
    client = hm.from_env()
    return (client,)


@app.cell
def _(client, hm, mo):
    browser = hm.table_browser(client)
    editor = hm.sql_editor(
        client,
        default_sql="SELECT 1 AS ok",
    )
    return browser, editor


@app.cell
def _(browser, editor, mo):
    return mo.vstack([browser.ui, editor.ui], gap=2)


@app.cell
def _(editor, hm):
    # Explicitly touch nested widget values so Marimo reruns this cell on clicks.
    _run = editor.run.value
    _rerun = editor.rerun.value
    _clear = editor.clear.value
    return hm.query_result(editor.result), _clear, _rerun, _run


if __name__ == "__main__":
    app.run()
