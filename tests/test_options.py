from __future__ import annotations

from types import SimpleNamespace

from hotdata_marimo.display import _option_map_with_unique_labels
from hotdata_marimo.table_browser import _connection_options


def test_option_map_with_unique_labels_keeps_all_values():
    options = _option_map_with_unique_labels(
        [("dup", "a"), ("dup", "b"), ("dup", "c")]
    )
    assert options == {
        "dup": "a",
        "dup (2)": "b",
        "dup (3)": "c",
    }


def test_connection_options_disambiguates_duplicate_names():
    conns = [
        SimpleNamespace(name="Warehouse", id="conn_1"),
        SimpleNamespace(name="Warehouse", id="conn_2"),
        SimpleNamespace(name="Analytics", id="conn_3"),
    ]
    options = _connection_options(conns)
    assert options == {
        "Warehouse": "conn_1",
        "Warehouse (conn_2)": "conn_2",
        "Analytics": "conn_3",
    }
