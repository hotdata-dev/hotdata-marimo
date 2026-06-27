from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from hotdata_framework import QueryResult


@pytest.fixture
def sample_result() -> QueryResult:
    return QueryResult(
        columns=["n"],
        rows=[[1]],
        row_count=1,
        result_id="res_1",
        query_run_id="run_1",
        execution_time_ms=10,
        warning=None,
        error_message=None,
    )


@pytest.fixture
def mock_client(sample_result: QueryResult):
    client = MagicMock()
    client.workspace_id = "ws_test"
    client.host = "https://api.hotdata.dev"
    client.session_id = "sb_1"
    client.execute_sql = MagicMock(return_value=sample_result)
    client.connections.return_value.list_connections.return_value = SimpleNamespace(
        connections=[]
    )
    client.list_managed_databases.return_value = []
    return client
