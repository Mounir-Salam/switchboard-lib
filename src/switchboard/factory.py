from switchboard.config import settings
from switchboard.connectors.blob_storage.localfs import LocalFSConnector
from switchboard.connectors.blob_storage.minio import MinioConnector
from switchboard.connectors.db_engines.duckdb import DuckDBConnector
from switchboard.connectors.db_engines.postgres import PostgresConnector
from switchboard.connectors.db_engines.clickhouse import ClickHouseConnector

class Switchboard:
    # Registries to hold active connections
    _storage_instances = {}
    _db_instances = {}
    
    @classmethod
    def get_storage(cls, name: str = "default", storage_type: str = None, path_or_bucket: str = None):
        """
        Retrieves or creates a named storage connection.
        If parameters aren't provided, it falls back to .env defaults.
        """
        if name in cls._storage_instances:
            return cls._storage_instances[name]

        # Fallbacks to settings
        st_type = storage_type or settings.STORAGE_TYPE
        
        if st_type == "LOCAL":
            path = path_or_bucket or settings.LOCAL_STORAGE_PATH
            instance = LocalFSConnector(path)
        elif st_type == "MINIO":
            # MinIO requires more configuration, so it will still use settings for keys
            instance = MinioConnector(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                bucket=path_or_bucket or settings.MINIO_BUCKET_NAME
            )
        else:
            raise ValueError(f"Unsupported storage type: {st_type}")

        cls._storage_instances[name] = instance
        return instance
    
    @classmethod
    def get_db(cls, name: str = "default", db_type: str = None, connection_string: str = None):
        """
        Retrieves or creates a named database connection.
        """
        if name in cls._db_instances:
            return cls._db_instances[name]

        # Fallbacks to settings
        engine_type = db_type or settings.DB_TYPE

        if engine_type == "DUCKDB":
            path = connection_string or settings.DUCKDB_PATH
            instance = DuckDBConnector(path)
        elif engine_type == "POSTGRES":
            url = connection_string or settings.POSTGRES_URL
            instance = PostgresConnector(url)
        elif engine_type == "CLICKHOUSE":
            # For simplicity, if a custom connection string is passed, we could parse it,
            # but for now we will leverage our settings or expect default connections.
            instance = ClickHouseConnector(
                host=settings.CLICKHOUSE_HOST,
                port=settings.CLICKHOUSE_PORT,
                user=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD
            )
        else:
            raise ValueError(f"Unsupported DB type: {engine_type}")

        cls._db_instances[name] = instance
        return instance