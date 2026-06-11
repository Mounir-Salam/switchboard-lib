import structlog
import pandas as pd
from sqlalchemy import create_engine, text
from switchboard.base.database import DatabaseProvider

class PostgresConnector(DatabaseProvider):
    def __init__(self, connection_url: str):
        self.url = connection_url
        
        self.logger = structlog.get_logger("switchboard.postgres").bind(
            connection_url = connection_url,
            provider = "POSTGRES"
        )
        
        self.engine = create_engine(self.url)
        
        self.connection = self.engine.connect()

    def execute(self, query: str):
        self.logger.info("Executing query")
        
        self.connection.execute(text(query))

    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        self.logger.info("Generating dataframe from query")
        
        return pd.read_sql(text(query), self.connection)
    
    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        self.logger.info("Writing table", table_name = table_name)
        
        df.to_sql(table_name, self.connection, if_exists = mode, index = False)

    def close(self) -> None:
        """Safely drops the network connection back to the database server."""
        if hasattr(self, "connection") and self.connection is not None:
            self.logger.info("Closing active Postgres database session")
            try:
                self.connection.close()
                self.engine.dispose() # Tethers off the global background pool completely
            except Exception as e:
                self.logger.warning("Error encountered while disposing engine", error = str(e))