import structlog
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from switchboard.base.database import DatabaseProvider

class PostgresConnector(DatabaseProvider):
    def __init__(self, connection_url: str):
        self.url = connection_url
        
        self.logger = structlog.get_logger("switchboard.postgres").bind(
            connection_url = connection_url,
            provider = "POSTGRES"
        )

    def execute(self, query: str):
        self.logger.info("Executing query")
        
        with psycopg2.connect(self.url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()

    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        self.logger.info("Generating dataframe from query")
        
        with psycopg2.connect(self.url) as conn:
            return pd.read_sql(query, conn)
    
    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        self.logger.info("Writing table", table_name = table_name)
        
        engine = create_engine(self.url)
        df.to_sql(table_name, engine, if_exists = mode, index = False)