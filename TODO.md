# hotdata-marimo — next steps

## Near term (build on MVP)

- [x] **Workspace selector** — When `HOTDATA_WORKSPACE` is unset and multiple workspaces exist, expose `mo.ui.dropdown` (or similar) and rebuild the client when the choice changes.
- [x] **Connection status** — Small status chip (API reachable, workspace id, optional sandbox) using a lightweight health or `workspaces`/`connections` probe.
- [ ] **Query cancel** — Wire cancel to the query-run API if/when exposed in the OpenAPI client; surface a Cancel control next to Run.
- [x] **`mo.ui.hotdata_*` aliases** — Re-export or thin wrappers: `hotdata_sql_editor`, `hotdata_table_browser`, `hotdata_query_result`, `hotdata_connection_picker` for discoverability.
- [x] **Tests** — Unit tests with mocked SDK responses; optional integration tests gated on `HOTDATA_API_KEY` (mirror sdk-python patterns).

## SQL editor & execution

- [ ] **Schema-aware autocomplete** — anywidget (or CodeMirror) + Hotdata `information_schema` / column metadata for table/column suggestions.
- [x] **Async UX** — Progress text or spinner while polling query runs; optional configurable timeouts.
- [x] **Run history panel** — `QueryRunsApi.list_query_runs` + metadata (latency, touched tables, `result_id`) in a side panel or collapsible.
- [x] **Rerun / clear** — Explicit rerun without relying only on `run_button` semantics; optional “clear result” action.

## Results

- [x] **Pagination / LIMIT guidance** — Surface row counts vs limit; warn when result is truncated if the API exposes it.
- [ ] **Export** — CSV / Parquet download links or buttons (align with Hotdata results/export APIs when available).
- [x] **Cached result reuse** — Prefer `get_result(result_id)` over re-running identical SQL when `result_id` is known.
- [ ] **Materialization / cache status** — Show persistence state when the API returns it (`processing` / `ready` / errors).

## Data discovery

- [x] **Connection picker** — Filter catalog by connection; map display names to ids consistently.
- [x] **Schema search** — Text filter over tables/columns without loading full dropdowns for huge catalogs.
- [ ] **Table preview** — `LIMIT` preview query from browser selection (optional second query).
- [ ] **Generated queries** — Starters beyond `SELECT *`: profile/join templates from selected tables.

## App mode

- [ ] **Deployable Marimo app** — Layout recipe (sidebar explorer + editor + result) and docs for `marimo run` / WASM constraints.
- [ ] **Auth in apps** — Document env injection for deployed apps; avoid embedding API keys in notebooks.

## Docs & packaging

- [x] **README** — Install, env vars, minimal notebook example, and “two-cell” pattern for `editor.result` + `mo.stop`.
- [x] **Changelog** — Keep `CHANGELOG.md` once versions ship.
