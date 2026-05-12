import duckdb
import pandas as pd
from pathlib import Path
from switchboard.base.database import DatabaseProvider

class DuckDBConnector(DatabaseProvider):
    def __init__(self, database_path: str = ":memory:"):
        """Connects to a local DuckDB file or an in-memory instance."""
        if database_path != ":memory:":
            db_path = Path(database_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.conn = duckdb.connect(database_path)

    def execute(self, query: str):
        return self.conn.execute(query)

    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        return self.conn.execute(query).df()
    
    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        """A helper specific to DuckDB to quickly register and create tables."""
        self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")