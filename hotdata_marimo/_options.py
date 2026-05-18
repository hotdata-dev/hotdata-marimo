"""Shared dropdown option helpers for Marimo UI widgets."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import marimo as mo

from hotdata_runtime import HotdataClient


def unique_label_options(
    pairs: list[tuple[str, str]],
    *,
    disambiguate: Callable[[str, str, int], str] | None = None,
) -> dict[str, str]:
    """Build a label→value map, suffixing repeated labels when needed."""
    counts: dict[str, int] = {}
    options: dict[str, str] = {}
    for label, value in pairs:
        count = counts.get(label, 0)
        counts[label] = count + 1
        if count == 0:
            key = label
        elif disambiguate is not None:
            key = disambiguate(label, value, count)
        else:
            key = f"{label} ({count + 1})"
        options[key] = value
    return options


def empty_dropdown(
    *,
    label: str,
    message: str,
    full_width: bool = True,
):
    return mo.ui.dropdown(
        options={message: ""},
        label=label,
        full_width=full_width,
    )


def connection_options(conns: list[Any]) -> dict[str, str]:
    pairs = [(str(c.name), str(c.id)) for c in conns]
    return unique_label_options(
        pairs,
        disambiguate=lambda label, value, count: f"{label} ({value})",
    )


def connection_picker(
    client: HotdataClient,
    *,
    label: str = "Connection",
    full_width: bool = True,
):
    listing = client.connections().list_connections()
    conns = listing.connections
    if not conns:
        return empty_dropdown(
            label=label,
            message="(no connections)",
            full_width=full_width,
        )
    return mo.ui.dropdown(
        options=connection_options(conns),
        label=label,
        full_width=full_width,
    )


def resolve_connection_picker(
    client: HotdataClient,
    *,
    label: str = "Connection",
    full_width: bool = True,
) -> tuple[Any | None, str | None]:
    """Return ``(dropdown_or_none, implicit_connection_id)`` for table browsers."""
    listing = client.connections().list_connections()
    conns = listing.connections
    if not conns:
        return None, ""
    if len(conns) == 1:
        return None, conns[0].id
    return connection_picker(client, label=label, full_width=full_width), None
