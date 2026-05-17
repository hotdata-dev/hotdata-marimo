from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import hotdata_marimo as hm
from hotdata_runtime import HotdataClient
from hotdata_marimo.sql_engine import HotdataMarimoEngine
from marimo._types.ids import VariableName


def test_register_hotdata_sql_engine_is_idempotent() -> None:
    from marimo._sql.get_engines import SUPPORTED_ENGINES

    hm.unregister_hotdata_sql_engine()
    assert SUPPORTED_ENGINES.count(HotdataMarimoEngine) == 0
    try:
        hm.register_hotdata_sql_engine()
        hm.register_hotdata_sql_engine()
        assert SUPPORTED_ENGINES.count(HotdataMarimoEngine) == 1
    finally:
        hm.unregister_hotdata_sql_engine()


def test_hotdata_engine_display_name_in_marimo_ui() -> None:
    hm.register_hotdata_sql_engine()
    try:
        client = MagicMock(spec=HotdataClient)
        client.connections.return_value.list_connections.return_value = (
            SimpleNamespace(connections=[])
        )
        engine = HotdataMarimoEngine(client, engine_name=VariableName("client"))
        import marimo._sql.get_engines as ge

        conn = ge.engine_to_data_source_connection(VariableName("client"), engine)
        assert conn.display_name == "Hotdata"

        import marimo._runtime.runner.hooks_post_execution as hpe

        conn_hpe = hpe.engine_to_data_source_connection(
            VariableName("client"), engine
        )
        assert conn_hpe.display_name == "Hotdata"
    finally:
        hm.unregister_hotdata_sql_engine()
