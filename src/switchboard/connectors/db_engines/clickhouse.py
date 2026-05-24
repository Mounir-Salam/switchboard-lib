import structlog
import clickhouse_connect
import pandas as pd
from switchboard.base.database import DatabaseProvider

class ClickHouseConnector(DatabaseProvider):
    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        
        self.logger = structlog.get_logger("switchboard.clickhouse").bind(
            provider = "CLICKHOUSE"
        )
        
        self.client = clickhouse_connect.get_client(
            host = self.host, port = self.port, username = self.user, password = self.password
        )

    def execute(self, query: str):
        self.logger.info("Executing query")
        
        self.client.command(query)

    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        self.logger.info("Generating dataframe from query")
        
        return self.client.query_df(query)

    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        self.logger.info("Writing table", table_name = table_name)
        
        if mode == "replace":
            self.client.command(f"DROP TABLE IF EXISTS {table_name}")
            
            # --- Map Pandas types to ClickHouse types dynamically ---
            columns = []
            for col_name, dtype in df.dtypes.items():
                if "int" in str(dtype):
                    ch_type = "Int64"
                elif "float" in str(dtype):
                    ch_type = "Float64"
                else:
                    ch_type = "String"  # Default fallback for objects/strings
                columns.append(f"{col_name} {ch_type}")
                
            columns_str = ", ".join(columns)
            create_query = f"CREATE TABLE {table_name} ({columns_str}) ENGINE = MergeTree() ORDER BY tuple()"
            self.client.command(create_query)
        
        self.client.insert_df(table_name, df)

    # 🤝 The Context Manager Teardown Hook
    def close(self) -> None:
        """Explicitly drops the network session when requested."""
        if hasattr(self, "client") and self.client is not None:
            self.logger.info("Closing active ClickHouse network session")
            try:
                self.client.close()
            except Exception as e:
                self.logger.warning("Error encountered while closing session", error=str(e))