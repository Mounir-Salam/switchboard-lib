import structlog
import pandas as pd
from sqlalchemy import create_engine, text
from switchboard.base.database import DatabaseProvider
from switchboard.utils.resilience import cloud_retry

class RedshiftConnector(DatabaseProvider):
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

        self.logger = structlog.get_logger("switchboard.redshift").bind(
            provider = "REDSHIFT",
            database = self.database,
            host = self.host
        )

        # Format: redshift+psycopg2://username:password@host:port/database
        self.connection_url = f"redshift+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        self.engine = create_engine(self.connection_url)
        self.connection = self.engine.connect()
        
        self.logger.info("Successfully established active Redshift connection session")

    def execute(self, query: str) -> None:
        self.logger.info("Executing relational statement")
        self.connection.execute(text(query))

    @cloud_retry(max_attempts = 4)
    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        self.logger.info("Generating dataframe from query engine")
        return pd.read_sql(text(query), self.connection)

    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace") -> None:
        """
        Note: For massive production data scaling, Redshift performs significantly
        better using a staging COPY format (S3 -> Redshift). This relational block
        handles micro to mid-scale structural pipeline drops natively.
        """
        self.logger.info("Writing batch data to table", table_name = table_name, execution_mode = mode)

        if mode == "replace":
            # TRUNCATE operations are completely idempotent.
            # If it fails halfway and retries, it just wipes the canvas and starts over.
            self._execute_upload_with_retry(df, table_name, mode)
        else:
            # APPEND operations are NOT safe to blindly retry.
            # We execute it exactly once. If it fails, we let it crash so the user can investigate.
            self._execute_upload_raw(df, table_name, mode)

    @cloud_retry(max_attempts = 4)
    def _execute_upload_with_retry(self, df: pd.DataFrame, table_name: str, mode: str) -> None:
        """Internal retriable method helper."""
        self._execute_upload_raw(df, table_name, mode)

    def _execute_upload_raw(self, df: pd.DataFrame, table_name: str, mode: str) -> None:
        """Single raw attempt execution path."""
        df.to_sql(
            name = table_name,
            con = self.connection,
            if_exists = mode,
            index = False,
            method = "multi"  # Batches inserts together to optimize network roundtrips
        )

    def close(self) -> None:
        """Safely tears down engine session connections."""
        if hasattr(self, "connection") and self.connection is not None:
            self.logger.info("Closing active Redshift database connection channels")
            try:
                self.connection.close()
                self.engine.dispose()
            except Exception as e:
                self.logger.warning("Error encountered while disposing Redshift engine pool", error = str(e))