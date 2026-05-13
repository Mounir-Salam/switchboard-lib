from switchboard.config import settings
from switchboard.connectors.blob_storage.localfs import LocalFSConnector
from switchboard.connectors.db_engines.duckdb import DuckDBConnector
from switchboard.connectors.db_engines.postgres import PostgresConnector
from switchboard.connectors.blob_storage.minio import MinioConnector

class Switchboard:
    @staticmethod
    def get_storage():
        if settings.STORAGE_TYPE == "LOCAL":
            return LocalFSConnector(settings.LOCAL_STORAGE_PATH)
        if settings.STORAGE_TYPE == "MINIO":
            return MinioConnector(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                bucket=settings.MINIO_BUCKET_NAME
            )
        raise ValueError(f"Unsupported storage type: {settings.STORAGE_TYPE}")

    @staticmethod
    def get_db():
        if settings.DB_TYPE == "DUCKDB":
            return DuckDBConnector(settings.DUCKDB_PATH)
        if settings.DB_TYPE == "POSTGRES":
            return PostgresConnector(settings.POSTGRES_URL)
        raise ValueError(f"Unsupported DB type: {settings.DB_TYPE}")