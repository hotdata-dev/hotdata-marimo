# hotdata-marimo

[Marimo](https://marimo.io/) widgets for [Hotdata](https://hotdata.dev) — run SQL, browse your schema, and work with managed databases in reactive notebooks.

## Install

```bash
pip install hotdata-marimo
```

## Authentication

Set `HOTDATA_API_KEY` in your environment. Optionally set `HOTDATA_WORKSPACE` to pin a specific workspace (the first available workspace is used if unset).

## Quickstart

Because Marimo reruns cells reactively, construct a widget in one cell and read its `.ui` or `.result` in the next.

```python
# Cell 1
import hotdata_marimo as hm

client = hm.from_env()
editor = hm.sql_editor(client, default_sql="SELECT 1 AS ok")
return editor.ui
```

```python
# Cell 2
return hm.query_result(editor.result)
```

Click **Run on Hotdata** after editing SQL. The editor caches the last successful result so downstream cells don't re-query on every refresh.

## Workspace selection

If you have multiple workspaces or `HOTDATA_WORKSPACE` is unset, add an interactive picker. `ws.client` updates when the selection changes:

```python
ws = hm.workspace_selector_from_env()
client = ws.client
return ws.ui
```

## Native Marimo SQL cells

Register the Hotdata engine once and Hotdata will appear as a selectable engine in the SQL connection picker:

```python
# Setup cell
import marimo as mo
import hotdata_marimo as hm

hm.register_hotdata_sql_engine()
client = hm.from_env()
```

```python
# Any SQL cell
_df = mo.sql("SELECT * FROM orders LIMIT 10", engine=client)
```

![Marimo SQL cell with Hotdata selected in the database connections picker](docs/images/mo-sql-hotdata-connection.png)

## Browse your schema

The table browser lets you pick a connection, search for a table, and inspect its columns — with a starter query ready to copy:

```python
browser = hm.table_browser(client)
return browser.ui
```

Use `browser.selected_table` in downstream cells to reference the chosen table.

## Managed databases

View existing managed databases and load new parquet files from a single tabbed panel:

```python
writer = hm.managed_database_writer(client)
return writer.tab_ui
```

Or show just the read-only panel:

```python
return hm.databases_panel(client)
```

## All widgets

| Widget | Code | What you get |
|--------|------|-------------|
| SQL editor | `hm.sql_editor(client)` | `.ui` to show the editor, `.result` to read rows |
| Query result | `hm.query_result(result)` | Renders a `QueryResult` as a table |
| Table browser | `hm.table_browser(client)` | Browse connections, tables, and column metadata |
| Managed databases | `hm.databases_panel(client)` | Read-only list of managed databases |
| Database writer | `hm.managed_database_writer(client)` | Create databases and load parquet files |
| Workspace picker | `hm.workspace_selector_from_env()` | Dropdown to switch workspaces |
| Connection picker | `hm.connection_picker(client)` | Dropdown of connections in the workspace |
| Connection status | `hm.connection_status(client)` | Health callout for the API and workspace |
| Connections panel | `hm.connections_panel(client)` | Status + list of connections |
| Recent results | `hm.recent_results(client)` | Browse past query results |
| Run history | `hm.run_history(client)` | Recent query runs |

All widgets are also available as `mo.ui.hotdata_*` aliases (e.g. `mo.ui.hotdata_sql_editor`) for discovery via Marimo's autocomplete.

## Demo notebook

```bash
uv run marimo edit examples/demo.py --no-token
```

The demo combines workspace selection, schema browsing, managed databases, query history, and a native SQL cell in a single tabbed interface.

## Development

```bash
uv sync --locked
uv run pytest
```
