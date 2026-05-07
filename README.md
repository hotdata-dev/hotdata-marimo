# hotdata-marimo

Marimo UI helpers for [Hotdata](https://hotdata.dev): run SQL from a notebook, browse catalog metadata, and render results as tables.

## Install

```bash
pip install hotdata-marimo
```

Requires Python 3.10+, plus the Hotdata Python SDK (`hotdata`) and `marimo`.

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `HOTDATA_API_KEY` | Yes | API key for the Hotdata API |
| `HOTDATA_API_URL` | No | API base URL (default: `https://api.hotdata.dev`) |
| `HOTDATA_WORKSPACE` | No | Workspace id; if unset, the first active workspace is used |
| `HOTDATA_SANDBOX` | No | Sandbox session id, passed through to the SDK |

## Minimal notebook

```python
import marimo as mo
import hotdata_marimo as hm

client = hm.from_env()
editor = hm.sql_editor(client, default_sql="SELECT 1 AS ok")
editor.ui
```

```python
result = editor.result
hm.query_result(result)
```

Importing `hotdata_marimo` registers discoverability aliases on Marimo’s UI namespace, so you can also use `mo.ui.hotdata_sql_editor`, `mo.ui.hotdata_table_browser`, `mo.ui.hotdata_query_result`, and `mo.ui.hotdata_connection_status`.

Use `hm.connection_status(client)` (or `mo.ui.hotdata_connection_status(client)`) for a small API/workspace health callout.

## Two-cell pattern

Keep the editor in one cell and consume `editor.result` in another. The editor caches the last successful run so downstream cells do not re-query the API on every refresh; click **Run on Hotdata** again after you change SQL. While a query is running, a Marimo status spinner is shown.

Marimo forbids reading the `.value` of a UI control in the **same** cell that created it. For `SqlEditor` / `TableBrowser`, **construct** the object in one cell (`editor = hm.sql_editor(...)`) and render **`.ui`** in a **later** cell (`editor.ui` or `mo.vstack([browser.ui, editor.ui])`).

See `examples/hotdata_basic.py` for a full notebook.

## Development

```bash
pip install -e .
marimo edit examples/hotdata_basic.py
```
