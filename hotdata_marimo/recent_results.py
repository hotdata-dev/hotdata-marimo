from __future__ import annotations

import marimo as mo

from hotdata_marimo.client import HotdataClient
from hotdata_marimo.result import QueryResult


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

