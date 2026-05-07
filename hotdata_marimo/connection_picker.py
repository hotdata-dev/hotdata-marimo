from __future__ import annotations

import marimo as mo

from hotdata_marimo.client import HotdataClient


def connection_picker(
    client: HotdataClient,
    *,
    label: str = "Connection",
    full_width: bool = True,
):
    listing = client.connections().list_connections()
    conns = listing.connections
    if not conns:
        return mo.ui.dropdown(
            options={"(no connections)": ""},
            label=label,
            full_width=full_width,
        )
    options = {c.name: c.id for c in conns}
    return mo.ui.dropdown(
        options=options,
        label=label,
        full_width=full_width,
    )

