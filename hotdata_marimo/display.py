"""Marimo views for query results, history, and workspace status."""

from __future__ import annotations

import marimo as mo

from hotdata_runtime import HotdataClient, QueryResult, workspace_health_lines


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
        self._rows: list[dict[str, object]] = [
            {
                "created_at": r.created_at,
                "status": r.status,
                "result_id": r.result_id,
            }
            for r in self._results
        ]
        self.table = (
            mo.ui.table(
                self._rows,
                label="Recent results",
                pagination=True,
                page_size=min(10, limit),
                selection="single",
                max_height=320,
            )
            if self._rows
            else None
        )

    @property
    def selected_result_id(self) -> str | None:
        if self.table is None:
            return None
        selected = self.table.value
        if not selected:
            return None
        row = selected[0]
        if not isinstance(row, dict):
            return None
        return row.get("result_id") or None

    @property
    def result(self) -> QueryResult:
        rid = self.selected_result_id
        mo.stop(rid is None, mo.md("Select a result row to load."))
        return self._client.get_result(rid)

    @property
    def result_panel(self):
        rid = self.selected_result_id
        if rid is None:
            return mo.md("_Select a result row to load._")
        return query_result(self._client.get_result(rid), label="Recent result")

    @property
    def tab_ui(self):
        if self.table is not None:
            _ = self.table.value
        return mo.vstack([self.ui, self.result_panel], gap=2)

    @property
    def ui(self):
        if self.table is None:
            return mo.md("_No recent results._")
        _ = self.table.value
        return mo.vstack(
            [
                mo.md("### Recent results"),
                self.table,
            ],
            gap=1,
        )


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


def connections_panel(client: HotdataClient):
    """Workspace health callout plus a table of configured connections."""
    status = connection_status(client)
    conns = client.connections().list_connections().connections
    if not conns:
        return mo.vstack([status, mo.md("_No connections in this workspace._")], gap=1)
    rows: list[dict[str, object]] = []
    for c in conns:
        rows.append(
            {
                "name": c.name,
                "id": c.id,
                "source_type": getattr(c, "source_type", None),
            }
        )
    return mo.vstack(
        [
            status,
            mo.ui.table(
                rows,
                label="Connections",
                pagination=True,
                page_size=min(10, len(rows)),
                selection=None,
                max_height=320,
            ),
        ],
        gap=1,
    )
