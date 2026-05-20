from switchboard.config import settings

from switchboard.connectors.blob_storage.localfs import LocalFSConnector
from switchboard.connectors.blob_storage.minio import MinioConnector
from switchboard.connectors.blob_storage.gcs import GCSConnector

from switchboard.connectors.db_engines.duckdb import DuckDBConnector
from switchboard.connectors.db_engines.postgres import PostgresConnector
from switchboard.connectors.db_engines.clickhouse import ClickHouseConnector
from switchboard.connectors.db_engines.bigquery import BigQueryConnector

class Switchboard:
    # Registries to hold active connections
    _storage_instances = {}
    _db_instances = {}
    
    @classmethod
    def get_storage(cls, name: str = "default", storage_type: str = None, **kwargs):
        """
        Retrieves or creates a named storage connection.
        **kwargs allows passing engine-specific configs (e.g., bucket, endpoint, secret_key)
        """
        if name in cls._storage_instances:
            return cls._storage_instances[name]

        # Fallbacks to settings
        st_type = storage_type or settings.STORAGE_TYPE
        
        if st_type == "LOCAL":
            
            print("[Factory Storage] Using LocalFS storage. Data will be stored on the local filesystem.")
            print(f"[Factory Storage] Local storage path: {kwargs.get("path") or settings.LOCAL_STORAGE_PATH}")
            
            path = kwargs.get("path") or settings.LOCAL_STORAGE_PATH
            instance = LocalFSConnector(path)
            
        elif st_type == "MINIO":
            
            print("[Factory Storage] Using MinIO storage. Data will be stored on the MinIO server.")
            print(f"[Factory Storage] MinIO Endpoint: {kwargs.get('endpoint') or settings.MINIO_ENDPOINT}")
            print(f"[Factory Storage] MinIO Access Key: {kwargs.get('access_key') or settings.MINIO_ACCESS_KEY}")
            print(f"[Factory Storage] MinIO Bucket: {kwargs.get('bucket') or settings.MINIO_BUCKET_NAME}")
            
            instance = MinioConnector(
                endpoint=kwargs.get("endpoint") or settings.MINIO_ENDPOINT,
                access_key=kwargs.get("access_key") or settings.MINIO_ACCESS_KEY,
                secret_key=kwargs.get("secret_key") or settings.MINIO_SECRET_KEY,
                bucket=kwargs.get("bucket") or settings.MINIO_BUCKET_NAME
            )
        elif st_type == "GCS":
            
            print("[Factory Storage] Using Google Cloud Storage. Data will be stored in the specified GCS bucket.")
            print(f"[Factory Storage] GCS Bucket Name: {kwargs.get('bucket_name') or settings.GCS_BUCKET_NAME}")
            
            instance = GCSConnector(
                bucket_name=kwargs.get("bucket_name") or settings.GCS_BUCKET_NAME,
                credentials_path=kwargs.get("credentials_path") or settings.GOOGLE_APPLICATION_CREDENTIALS
            )
        
        else:
            raise ValueError(f"Unsupported storage type: {st_type}")

        cls._storage_instances[name] = instance
        return instance
    
    @classmethod
    def get_db(cls, name: str = "default", db_type: str = None, **kwargs):
        """
        Retrieves or creates a named database connection.
        **kwargs captures custom parameters like connection_string, host, or credentials_path.
        """
        if name in cls._db_instances:
            return cls._db_instances[name]

        # Fallbacks to settings
        engine_type = db_type or settings.DB_TYPE

        if engine_type == "DUCKDB":
            
            print("[Factory Database] Using DuckDB. Data will be stored in a local DuckDB file.")
            print(f"[Factory Database] DuckDB file path: {kwargs.get('connection_string') or settings.DUCKDB_PATH}")
            
            path = kwargs.get("connection_string") or settings.DUCKDB_PATH
            instance = DuckDBConnector(path)
            
        elif engine_type == "POSTGRES":
            
            print("[Factory Database] Using PostgreSQL. Data will be stored in the specified PostgreSQL database.")
            print(f"[Factory Database] PostgreSQL connection string: {kwargs.get('connection_string') or settings.POSTGRES_URL}")
            
            url = kwargs.get("connection_string") or settings.POSTGRES_URL
            instance = PostgresConnector(url)
            
        elif engine_type == "CLICKHOUSE":
            
            print("[Factory Database] Using ClickHouse. Data will be stored in the specified ClickHouse database.")
            print(f"[Factory Database] ClickHouse host: {kwargs.get('host') or settings.CLICKHOUSE_HOST}")
            print(f"[Factory Database] ClickHouse port: {kwargs.get('port') or settings.CLICKHOUSE_PORT}")
            print(f"[Factory Database] ClickHouse user: {kwargs.get('user') or settings.CLICKHOUSE_USER}")
            
            instance = ClickHouseConnector(
                host=kwargs.get("host") or settings.CLICKHOUSE_HOST,
                port=kwargs.get("port") or settings.CLICKHOUSE_PORT,
                user=kwargs.get("user") or settings.CLICKHOUSE_USER,
                password=kwargs.get("password") or settings.CLICKHOUSE_PASSWORD
            )
            
        elif engine_type == "BIGQUERY":            
            
            print("[Factory Database] Using BigQuery. Data will be stored in the specified BigQuery dataset.")
            print(f"[Factory Database] BigQuery project ID: {kwargs.get('project_id') or settings.BQ_PROJECT_ID}")
            print(f"[Factory Database] BigQuery dataset ID: {kwargs.get('dataset_id') or settings.BQ_DATASET_ID}")
            
            instance = BigQueryConnector(
                project_id=kwargs.get("project_id") or settings.BQ_PROJECT_ID,
                dataset_id=kwargs.get("dataset_id") or settings.BQ_DATASET_ID,
                credentials_path=kwargs.get("credentials_path") or settings.GOOGLE_APPLICATION_CREDENTIALS
            )
        else:
            raise ValueError(f"Unsupported DB type: {engine_type}")

        cls._db_instances[name] = instance
        return instance