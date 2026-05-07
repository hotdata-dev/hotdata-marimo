"""Marimo views for query results, history, and workspace status."""

from __future__ import annotations

import marimo as mo

from hotdata_core_notebook.client import HotdataClient
from hotdata_core_notebook.health import workspace_health_lines
from hotdata_core_notebook.result import QueryResult


def query_result(
    result: QueryResult,
    *,
    label: str = "Hotdata result",
    page_size: int = 25,
    max_height: int = 480,
):
    shown_rows = len(result.rows)
    if result.row_count > shown_rows and shown_rows > 0:
        trunc = mo.callout(
            mo.md(
                f"Showing **{shown_rows}** of **{result.row_count}** rows. "
                "Consider adding a `LIMIT` clause for faster iteration."
            ),
            kind="warn",
        )
    else:
        trunc = None
    meta_bits = []
    if result.result_id:
        meta_bits.append(f"**result_id** `{result.result_id}`")
    if result.query_run_id:
        meta_bits.append(f"**query_run_id** `{result.query_run_id}`")
    if result.execution_time_ms is not None:
        meta_bits.append(f"**execution_time_ms** {result.execution_time_ms}")
    if result.warning:
        meta_bits.append(f"**warning** {result.warning}")
    if result.error_message:
        meta_bits.append(f"**error** {result.error_message}")
    header = mo.md(" · ".join(meta_bits) if meta_bits else "_No metadata._")
    df = result.to_pandas()
    tbl = mo.ui.table(
        df,
        label=label,
        pagination=True,
        page_size=page_size,
        selection=None,
        max_height=max_height,
    )
    summary = mo.md(f"**{result.row_count}** rows · **{len(result.columns)}** columns")
    bits = [summary]
    if trunc is not None:
        bits.append(trunc)
    bits.extend([header, tbl])
    return mo.vstack(bits, gap=1)


class RecentResults:
    def __init__(self, client: HotdataClient, *, limit: int = 50) -> None:
        self._client = client
        listing = client.results().list_results(limit=limit, offset=0)
        self._results = listing.results
        options = {
            f"{r.created_at} · {r.status} · {r.id}": r.id for r in self._results
        }
        self.pick = mo.ui.dropdown(
            options=options or {"(no results)": ""},
            label="Recent results",
            full_width=True,
        )

    @property
    def selected_result_id(self) -> str | None:
        v = self.pick.value
        return v if v else None

    @property
    def result(self) -> QueryResult:
        rid = self.selected_result_id
        mo.stop(rid is None, mo.md("Pick a result id to load."))
        return self._client.get_result(rid or "")

    @property
    def ui(self):
        _ = self.pick.value
        return mo.vstack([self.pick], gap=1)


def recent_results(client: HotdataClient, *, limit: int = 50) -> RecentResults:
    return RecentResults(client, limit=limit)


def run_history(
    client: HotdataClient,
    *,
    limit: int = 20,
    label: str = "Run history",
):
    runs = client.query_runs().list_query_runs(limit=limit).query_runs
    if not runs:
        return mo.md("_No query runs returned._")

    rows: list[dict[str, object]] = []
    for r in runs:
        rows.append(
            {
                "created_at": getattr(r, "created_at", None),
                "status": getattr(r, "status", None),
                "execution_time_ms": getattr(r, "execution_time_ms", None),
                "result_id": getattr(r, "result_id", None),
                "query_run_id": getattr(r, "id", None)
                or getattr(r, "query_run_id", None),
            }
        )

    return mo.vstack(
        [
            mo.md(f"### {label}"),
            mo.ui.table(
                rows,
                pagination=True,
                page_size=min(10, limit),
                selection=None,
                max_height=320,
            ),
        ],
        gap=1,
    )


def connection_status(client: HotdataClient):
    """Small status line: API reachability, workspace id, connection count, sandbox."""
    ok, parts = workspace_health_lines(client)
    if ok:
        return mo.callout(mo.md(" · ".join(parts)), kind="success")
    return mo.callout(
        mo.md(f"**API** error — {parts[0]}"),
        kind="danger",
    )
