from __future__ import annotations

import marimo as mo

from hotdata.exceptions import ApiException

from hotdata_marimo.client import HotdataClient


def connection_status(client: HotdataClient):
    """Small status line: API reachability, workspace id, connection count, sandbox."""
    try:
        listing = client.connections().list_connections()
        n = len(listing.connections)
        bits = [
            "**API** reachable",
            f"**workspace** `{client.workspace_id}`",
            f"**connections** {n}",
        ]
        if client.session_id:
            bits.append(f"**sandbox** `{client.session_id}`")
        return mo.callout(mo.md(" · ".join(bits)), kind="success")
    except ApiException as e:
        msg = e.reason or str(e)
        return mo.callout(
            mo.md(f"**API** error — {msg}"),
            kind="danger",
        )
