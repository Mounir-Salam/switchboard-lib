import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from switchboard.base.database import DatabaseProvider

class PostgresConnector(DatabaseProvider):
    def __init__(self, connection_url: str):
        self.url = connection_url
        # We don't open the connection here to avoid keeping it 
        # open forever, but you could if you prefer a persistent session.

    def execute(self, query: str):
        with psycopg2.connect(self.url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()

    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        with psycopg2.connect(self.url) as conn:
            return pd.read_sql(query, conn)
    
    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        engine = create_engine(self.url)
        df.to_sql(table_name, engine, if_exists=mode, index=False)