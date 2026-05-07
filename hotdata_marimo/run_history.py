from __future__ import annotations

import marimo as mo

from hotdata_marimo.client import HotdataClient


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
                "query_run_id": getattr(r, "id", None) or getattr(r, "query_run_id", None),
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

