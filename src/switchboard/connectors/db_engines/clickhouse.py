import clickhouse_connect
import pandas as pd
from switchboard.base.database import DatabaseProvider

class ClickHouseConnector(DatabaseProvider):
    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def _get_client(self):
        return clickhouse_connect.get_client(
            host=self.host, port=self.port, username=self.user, password=self.password
        )

    def execute(self, query: str):
        client = self._get_client()
        client.command(query)

    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        client = self._get_client()
        return client.query_df(query)

    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        client = self._get_client()
        
        if mode == "replace":
            client.command(f"DROP TABLE IF EXISTS {table_name}")
            
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
            
            # ClickHouse requires an ENGINE. 'MergeTree' is the standard production engine.
            # It also requires an ORDER BY clause. We can just use 'tuple()' (no specific key) for generic inputs.
            create_query = f"CREATE TABLE {table_name} ({columns_str}) ENGINE = MergeTree() ORDER BY tuple()"
            client.command(create_query)
        
        # Now that the table definitely exists, we safely insert the data!
        client.insert_df(table_name, df)