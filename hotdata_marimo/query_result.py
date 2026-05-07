from __future__ import annotations

import marimo as mo

from hotdata_marimo.result import QueryResult


def query_result(
    result: QueryResult,
    *,
    label: str = "Hotdata result",
    page_size: int = 25,
    max_height: int = 480,
):
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
    return mo.vstack([summary, header, tbl], gap=1)
