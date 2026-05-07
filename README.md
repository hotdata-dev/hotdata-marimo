# hotdata-marimo

Marimo UI helpers for [Hotdata](https://hotdata.dev): run SQL from a notebook, browse catalog metadata, and render results as tables.

## Install

```bash
pip install hotdata-marimo
```

Requires Python 3.10+, **Marimo**, and [**hotdata-core-notebook**](https://github.com/hotdata-dev/hotdata-notebook-core) (Hotdata SDK + shared client — pulled in automatically when you `pip install hotdata-marimo`).

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
return editor.ui
```

```python
return hm.query_result(editor.result)
```

Importing `hotdata_marimo` registers discoverability aliases on Marimo’s UI namespace, so you can also use `mo.ui.hotdata_sql_editor`, `mo.ui.hotdata_table_browser`, `mo.ui.hotdata_query_result`, and `mo.ui.hotdata_connection_status`.

Use `hm.connection_status(client)` (or `mo.ui.hotdata_connection_status(client)`) for a small API/workspace health callout.

## Two-cell pattern

Keep the editor in one cell and consume `editor.result` in another. The editor caches the last successful run so downstream cells do not re-query the API on every refresh; click **Run on Hotdata** again after you change SQL. While a query is running, a Marimo status spinner is shown.

Marimo only shows **what you `return` from a cell**. Calling `mo.vstack(...)` or `hm.query_result(...)` without returning it produces no visible output.

See `examples/hotdata_basic.py` for a full notebook: five Python cells (`mo.vstack` for **controls only**, then a separate cell `return hm.query_result(editor.result)` so results show immediately — **avoid** `mo.lazy` here: it only renders after the block scrolls into view, which looks like an empty cell). If Marimo shows **empty cells**, quit and remove `examples/__marimo__/` so the UI reloads from the `.py` file only.

## Layout

This repo is intentionally thin: **API client, env helpers, and result models** live in **hotdata-core-notebook**; **hotdata-marimo** only adds Marimo widgets (`sql_editor`, `table_browser`, `display` for tables/status/history, `workspace_selector`). Import `HotdataClient` / `QueryResult` / `from_env` from **`hotdata_marimo`** or directly from **`hotdata_core_notebook`**.

## Development

This package depends on [**hotdata-notebook-core**](https://github.com/hotdata-dev/hotdata-notebook-core) (PyPI name `hotdata-core-notebook`). Install pulls it straight from GitHub until it is published:

```bash
pip install -e .
marimo edit examples/hotdata_basic.py --no-token
```

To pin a branch or commit, override the dependency when installing, for example:

```bash
pip install "hotdata-core-notebook @ git+https://github.com/hotdata-dev/hotdata-notebook-core.git@main"
pip install -e .
```

If the repo is **private**, use SSH (with keys configured) or HTTPS with a credential helper:

```bash
pip install "hotdata-core-notebook @ git+ssh://git@github.com/hotdata-dev/hotdata-notebook-core.git"
pip install -e .
```

The **`[project] name`** in [hotdata-notebook-core](https://github.com/hotdata-dev/hotdata-notebook-core) `pyproject.toml` must stay **`hotdata-core-notebook`** so it matches this dependency line and the import package **`hotdata_core_notebook`**.

Use **`--no-token`** for local development so the editor does not redirect to `/auth/login` (session auth is easy to hit with a global Marimo config). For a public or shared machine, omit it and use the printed URL with an access token instead.
