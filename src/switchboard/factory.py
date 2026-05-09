from switchboard.config import settings
from switchboard.connectors.blob_storage.localfs import LocalFSConnector
from switchboard.connectors.db_engines.duckdb import DuckDBConnector

class Switchboard:
    @staticmethod
    def get_storage():
        if settings.STORAGE_TYPE == "LOCAL":
            return LocalFSConnector(settings.LOCAL_STORAGE_PATH)
        # We can add S3/Minio logic here later
        raise ValueError(f"Unsupported storage type: {settings.STORAGE_TYPE}")

    @staticmethod
    def get_db():
        if settings.DB_TYPE == "DUCKDB":
            return DuckDBConnector(settings.DUCKDB_PATH)
        # We can add Postgres/Snowflake logic here later
        raise ValueError(f"Unsupported DB type: {settings.DB_TYPE}")