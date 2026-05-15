# hotdata-marimo

Marimo UI helpers for [Hotdata](https://hotdata.dev): run SQL from a notebook, browse catalog metadata, and render results as tables.

## Install

```bash
uv pip install hotdata-marimo
# or: pip install hotdata-marimo
```

Requires Python 3.10+, **Marimo**, and [**hotdata-runtime**](https://github.com/hotdata-dev/hotdata-runtime) (Hotdata SDK + runtime/session semantics — pulled in automatically when you `pip install hotdata-marimo`).

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

## Examples

- `examples/hotdata_basic.py` — end-to-end editor + browser + result rendering flow.

Run:

```bash
marimo edit examples/hotdata_basic.py --no-token
```

## Layout

This repo is intentionally thin: **API client, env helpers, and result models** live in **hotdata-runtime**; **hotdata-marimo** only adds Marimo widgets (`sql_editor`, `table_browser`, `display` for tables/status/history, `workspace_selector`). Import `HotdataClient` / `QueryResult` / `from_env` from **`hotdata_marimo`** or directly from **`hotdata_runtime`**.

## Development

This package depends on [**hotdata-runtime**](https://github.com/hotdata-dev/hotdata-runtime) (PyPI name `hotdata-runtime`). Development uses **uv**; keep a sibling checkout at `../hotdata-runtime` so the lockfile resolves the runtime from disk (see `[tool.uv.sources]` in `pyproject.toml`).

```bash
uv sync --locked
uv run pytest
marimo edit examples/hotdata_basic.py --no-token
```

To pin **hotdata-runtime** from Git instead of the sibling path, remove the `[tool.uv.sources]` block, set the dependency line as needed, and run `uv lock` again.

For a **publishable** `uv.lock` (CI that only clones this repo), remove `[tool.uv.sources]`, point `hotdata-runtime` at PyPI or `git+https://…`, then `uv lock`.

The **`[project] name`** in [hotdata-runtime](https://github.com/hotdata-dev/hotdata-runtime) `pyproject.toml` is **`hotdata-runtime`** and the import package is **`hotdata_runtime`**.

Use **`--no-token`** for local development so the editor does not redirect to `/auth/login` (session auth is easy to hit with a global Marimo config). For a public or shared machine, omit it and use the printed URL with an access token instead.
