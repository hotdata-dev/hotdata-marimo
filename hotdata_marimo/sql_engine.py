"""Marimo ``mo.sql`` engine integration for :class:`~hotdata_runtime.HotdataClient`."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal

from hotdata_runtime import HotdataClient

from marimo import _loggers
from marimo._data.models import (
    Database,
    DataSourceConnection,
    DataTable,
    DataTableColumn,
    Schema,
)
from marimo._sql.engines.types import InferenceConfig, SQLConnection
from marimo._sql.utils import convert_to_output, sql_type_to_data_type
from marimo._types.ids import VariableName

LOGGER = _loggers.marimo_logger()


def _table_schema_name(t: Any) -> str:
    return str(t.var_schema)


class HotdataMarimoEngine(SQLConnection[HotdataClient]):
    """Marimo :class:`~marimo._sql.engines.types.SQLConnection` backed by Hotdata.

    Catalog methods support Marimo's Data Sources panel. ``execute()`` only runs SQL
    via :meth:`~hotdata_runtime.HotdataClient.execute_sql` (no catalog calls in that path).
    """

    def __init__(
        self,
        connection: HotdataClient,
        engine_name: VariableName | None = None,
    ) -> None:
        super().__init__(connection, engine_name)
        self._connections_cache: list[Any] | None = None
        self._connection_id_cache: dict[str, str] | None = None

    @property
    def source(self) -> str:
        return "hotdata"

    @property
    def dialect(self) -> str:
        # Marimo labels engines as ``{dialect} ({variable_name})``; display_name is patched to "Hotdata".
        return "hotdata"

    @staticmethod
    def is_compatible(var: Any) -> bool:
        return isinstance(var, HotdataClient)

    @property
    def inference_config(self) -> InferenceConfig:
        return InferenceConfig(
            auto_discover_schemas=True,
            auto_discover_tables="auto",
            auto_discover_columns="auto",
        )

    def _resolve_should_auto_discover(
        self,
        value: bool | Literal["auto"],
    ) -> bool:
        if value == "auto":
            return True
        return value

    def _connection_ids(self) -> dict[str, str]:
        if self._connection_id_cache is None:
            self._connection_id_cache = {
                str(c.name): str(c.id) for c in self._connections()
            }
        return self._connection_id_cache

    def _connection_id(self, connection_name: str) -> str | None:
        return self._connection_ids().get(connection_name)

    def _connections(self) -> list[Any]:
        if self._connections_cache is None:
            self._connections_cache = list(
                self._connection.connections().list_connections().connections
            )
        return self._connections_cache

    def _iter_grouped(
        self,
        *,
        connection_id: str | None,
        include_columns: bool,
    ) -> dict[str, dict[str, list[Any]]]:
        grouped: dict[str, dict[str, list[Any]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for t in self._connection.iter_tables(
            connection_id=connection_id,
            include_columns=include_columns,
        ):
            grouped[str(t.connection)][_table_schema_name(t)].append(t)
        return grouped

    def get_default_database(self) -> str | None:
        listing = self._connections()
        if not listing:
            return None
        return str(listing[0].name)

    def get_default_schema(self) -> str | None:
        return None

    def get_databases(
        self,
        *,
        include_schemas: bool | Literal["auto"],
        include_tables: bool | Literal["auto"],
        include_table_details: bool | Literal["auto"],
    ) -> list[Database]:
        databases: list[Database] = []
        for c in self._connections():
            name = str(c.name)
            if self._resolve_should_auto_discover(include_schemas):
                schemas = self.get_schemas(
                    database=name,
                    include_tables=self._resolve_should_auto_discover(
                        include_tables
                    ),
                    include_table_details=self._resolve_should_auto_discover(
                        include_table_details
                    ),
                )
            else:
                schemas = []
            databases.append(
                Database(
                    name=name,
                    dialect=self.dialect,
                    schemas=schemas,
                    engine=self._engine_name,
                )
            )
        return databases

    def get_schemas(
        self,
        *,
        database: str | None,
        include_tables: bool,
        include_table_details: bool,
    ) -> list[Schema]:
        if not database:
            return []
        conn_id = self._connection_id(database)
        if conn_id is None:
            LOGGER.warning("Unknown Hotdata connection name %r", database)
            return []
        grouped = self._iter_grouped(
            connection_id=conn_id,
            include_columns=include_table_details,
        )
        inner = grouped.get(database, {})
        schemas: list[Schema] = []
        for schema_name in sorted(inner.keys()):
            tables: list[DataTable] = []
            if include_tables:
                tables = self.get_tables_in_schema(
                    schema=schema_name,
                    database=database,
                    include_table_details=include_table_details,
                )
                if not tables:
                    continue
            schemas.append(Schema(name=schema_name, tables=tables))
        return schemas

    def _data_table_from_table_info(self, t: Any) -> DataTable:
        cols: list[DataTableColumn] = []
        for col in t.columns or []:
            cols.append(
                DataTableColumn(
                    name=str(col.name),
                    type=sql_type_to_data_type(str(col.data_type)),
                    external_type=str(col.data_type),
                    sample_values=[],
                )
            )
        return DataTable(
            source_type="connection",
            source=self.source,
            name=str(t.table),
            num_rows=None,
            num_columns=len(cols) if cols else None,
            variable_name=None,
            engine=self._engine_name,
            type="table",
            columns=cols,
            primary_keys=None,
            indexes=None,
        )

    def get_tables_in_schema(
        self,
        *,
        schema: str,
        database: str,
        include_table_details: bool,
    ) -> list[DataTable]:
        conn_id = self._connection_id(database)
        if conn_id is None:
            return []
        grouped = self._iter_grouped(
            connection_id=conn_id,
            include_columns=include_table_details,
        )
        tables_info = grouped.get(database, {}).get(schema, [])
        out: list[DataTable] = []
        for t in sorted(tables_info, key=lambda x: str(x.table)):
            if include_table_details:
                if t.columns:
                    out.append(self._data_table_from_table_info(t))
                    continue
                dt = self.get_table_details(
                    table_name=str(t.table),
                    schema_name=schema,
                    database_name=database,
                )
                if dt is not None:
                    out.append(dt)
            else:
                out.append(
                    DataTable(
                        source_type="connection",
                        source=self.source,
                        name=str(t.table),
                        num_rows=None,
                        num_columns=len(t.columns or []) if t.columns else None,
                        variable_name=None,
                        engine=self._engine_name,
                        type="table",
                        columns=[],
                        primary_keys=None,
                        indexes=None,
                    )
                )
        return out

    def get_table_details(
        self,
        *,
        table_name: str,
        schema_name: str,
        database_name: str,
    ) -> DataTable | None:
        conn_id = self._connection_id(database_name)
        if conn_id is None:
            return None
        qualified = f"{database_name}.{schema_name}.{table_name}"
        try:
            cols_raw = self._connection.columns_for_qualified(
                qualified, connection_id=conn_id
            )
        except Exception:
            LOGGER.warning(
                "Failed to load columns for %s",
                qualified,
                exc_info=True,
            )
            return None
        cols: list[DataTableColumn] = []
        for col in cols_raw:
            cols.append(
                DataTableColumn(
                    name=str(col.name),
                    type=sql_type_to_data_type(str(col.data_type)),
                    external_type=str(col.data_type),
                    sample_values=[],
                )
            )
        return DataTable(
            source_type="connection",
            source=self.source,
            name=table_name,
            num_rows=None,
            num_columns=len(cols),
            variable_name=None,
            engine=self._engine_name,
            type="table",
            columns=cols,
            primary_keys=None,
            indexes=None,
        )

    def execute(self, query: str) -> Any:
        qr = self._connection.execute_sql(query)
        fmt = self.sql_output_format()

        def to_polars() -> Any:
            import polars as pl

            if not qr.columns:
                return pl.DataFrame()
            return pl.DataFrame(qr.rows, schema=qr.columns, orient="row")

        return convert_to_output(
            sql_output_format=fmt,
            to_polars=to_polars,
            to_pandas=qr.to_pandas,
            to_native=to_polars,
        )


_HOTDATA_ENGINE_DISPLAY_NAME = "Hotdata"
_ORIGINAL_ENGINE_TO_CONNECTION = None


def _install_hotdata_engine_display_name() -> None:
    """Show ``Hotdata`` in Marimo's SQL engine / Data Sources UI (not ``sql (client)``)."""
    global _ORIGINAL_ENGINE_TO_CONNECTION
    if _ORIGINAL_ENGINE_TO_CONNECTION is not None:
        return

    import marimo._sql.get_engines as ge

    _ORIGINAL_ENGINE_TO_CONNECTION = ge.engine_to_data_source_connection

    def engine_to_data_source_connection(
        variable_name: VariableName, engine: object
    ) -> DataSourceConnection:
        conn = _ORIGINAL_ENGINE_TO_CONNECTION(variable_name, engine)  # type: ignore[arg-type]
        if not isinstance(engine, HotdataMarimoEngine):
            return conn
        return DataSourceConnection(
            source=conn.source,
            dialect=conn.dialect,
            name=conn.name,
            display_name=_HOTDATA_ENGINE_DISPLAY_NAME,
            databases=conn.databases,
            default_database=conn.default_database,
            default_schema=conn.default_schema,
        )

    _set_engine_to_data_source_connection(engine_to_data_source_connection)


def _set_engine_to_data_source_connection(fn: object) -> None:
    """Marimo imports this helper in multiple modules; patch all bindings."""
    import marimo._runtime.runner.hooks_post_execution as hpe
    import marimo._runtime.runtime as rt
    import marimo._sql.get_engines as ge

    ge.engine_to_data_source_connection = fn  # type: ignore[assignment]
    hpe.engine_to_data_source_connection = fn  # type: ignore[assignment]
    rt.engine_to_data_source_connection = fn  # type: ignore[assignment]


def register_hotdata_sql_engine() -> None:
    """Register :class:`HotdataMarimoEngine` with Marimo's SQL engine registry (idempotent)."""
    _install_hotdata_engine_display_name()
    from marimo._sql.get_engines import SUPPORTED_ENGINES

    if HotdataMarimoEngine in SUPPORTED_ENGINES:
        return
    SUPPORTED_ENGINES.insert(0, HotdataMarimoEngine)


def unregister_hotdata_sql_engine() -> None:
    """Remove :class:`HotdataMarimoEngine` from Marimo's registry (mostly for tests)."""
    from marimo._sql.get_engines import SUPPORTED_ENGINES

    while HotdataMarimoEngine in SUPPORTED_ENGINES:
        SUPPORTED_ENGINES.remove(HotdataMarimoEngine)
