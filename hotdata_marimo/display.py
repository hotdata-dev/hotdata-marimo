"""Marimo views for query results, history, and workspace status."""

from __future__ import annotations

import marimo as mo

from hotdata_runtime import HotdataClient, QueryResult, workspace_health_lines


def _option_map_with_unique_labels(
    pairs: list[tuple[str, str]],
) -> dict[str, str]:
    counts: dict[str, int] = {}
    options: dict[str, str] = {}
    for label, value in pairs:
        count = counts.get(label, 0)
        counts[label] = count + 1
        key = label if count == 0 else f"{label} ({count + 1})"
        options[key] = value
    return options


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
    meta = result.metadata_dict()
    meta_bits = []
    if meta["result_id"]:
        meta_bits.append(f"**result_id** `{meta['result_id']}`")
    if meta["query_run_id"]:
        meta_bits.append(f"**query_run_id** `{meta['query_run_id']}`")
    if meta["execution_time_ms"] is not None:
        meta_bits.append(f"**execution_time_ms** {meta['execution_time_ms']}")
    if meta["warning"]:
        meta_bits.append(f"**warning** {meta['warning']}")
    if meta["error_message"]:
        meta_bits.append(f"**error** {meta['error_message']}")
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
        self._results = client.list_recent_results(limit=limit, offset=0)
        option_pairs = [
            (f"{r.created_at} · {r.status} · {r.result_id}", r.result_id)
            for r in self._results
        ]
        options = _option_map_with_unique_labels(option_pairs)
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
    runs = client.list_run_history(limit=limit)
    if not runs:
        return mo.md("_No query runs returned._")

    rows: list[dict[str, object]] = []
    for r in runs:
        rows.append(
            {
                "created_at": r.created_at,
                "status": r.status,
                "execution_time_ms": r.execution_time_ms,
                "result_id": r.result_id,
                "query_run_id": r.query_run_id,
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
