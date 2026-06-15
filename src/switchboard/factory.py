import structlog

from switchboard.config import settings

from switchboard.connectors.blob_storage.localfs import LocalFSConnector
from switchboard.connectors.blob_storage.minio import MinioConnector
from switchboard.connectors.blob_storage.gcs import GCSConnector
from switchboard.connectors.blob_storage.s3 import S3Connector

from switchboard.connectors.db_engines.duckdb import DuckDBConnector
from switchboard.connectors.db_engines.postgres import PostgresConnector
from switchboard.connectors.db_engines.clickhouse import ClickHouseConnector
from switchboard.connectors.db_engines.bigquery import BigQueryConnector
from switchboard.connectors.db_engines.redshift import RedshiftConnector

from switchboard.utils.schemas import BigQueryConfig, GCSConfig, ClickHouseConfig, PostgresConfig, MinioConfig, S3Config, RedshiftConfig

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
        st_type = storage_type or settings.STORAGE_TYPE.upper()
        
        logger = structlog.get_logger("switchboard.factory").bind(
            provider = st_type
        )
        
        if st_type == "LOCAL":
            
            path = kwargs.get("path") or settings.LOCAL_STORAGE_PATH
            
            logger.info(
                "[Factory Storage] Using Local storage. Data will be stored on the local filesystem.",
                path = path
            )
            instance = LocalFSConnector(path)
            
        elif st_type == "MINIO":
            
            logger.info("[Factory Storage] Initializing storage provider")

            # Border Guard: Validate incoming arguments using our schema
            config = MinioConfig(
                endpoint = kwargs.get("endpoint") or settings.MINIO_ENDPOINT,
                access_key = kwargs.get("access_key") or settings.MINIO_ACCESS_KEY,
                secret_key = kwargs.get("secret_key") or settings.MINIO_SECRET_KEY,
                bucket_name = kwargs.get("bucket_name") or settings.MINIO_BUCKET_NAME
            )
            
            logger.info(
                "[Factory Storage] Storage provider configuration validated", 
                endpoint = config.endpoint,
                access_key = config.access_key,
                bucket = config.bucket_name
            )
            
            instance = MinioConnector(
                endpoint = config.endpoint,
                access_key = config.access_key,
                secret_key = config.secret_key,
                bucket_name = config.bucket_name
            )
        
        elif st_type == "GCS":
            
            logger.info("[Factory Storage] Initializing storage provider")
            
            # Border Guard: Validate incoming arguments using our schema
            config = GCSConfig(
                bucket_name = kwargs.get("bucket_name") or settings.GCS_BUCKET_NAME,
                credentials_path = kwargs.get("credentials_path") or settings.GOOGLE_APPLICATION_CREDENTIALS
            )
            
            logger.info(
                "[Factory Storage] Storage provider configuration validated", 
                bucket = config.bucket_name
            )
            
            instance = GCSConnector(
                bucket_name = config.bucket_name,
                credentials_path = config.credentials_path
            )
        
        elif st_type == "S3":
            logger.info("Initializing storage provider", provider = "S3")
            
            # Resolve arguments combining explicit kwargs and system configuration fallbacks
            config = S3Config(
                bucket_name = kwargs.get("bucket_name") or settings.AWS_S3_BUCKET_NAME,
                region_name = kwargs.get("region_name") or settings.AWS_REGION,
                access_key_id = kwargs.get("access_key") or settings.AWS_ACCESS_KEY_ID,
                secret_access_key = kwargs.get("secret_key") or settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url = kwargs.get("endpoint_url") or settings.AWS_ENDPOINT_URL
            )
            
            logger.info(
                "Storage provider configuration validated",
                provider = "S3",
                bucket = config.bucket_name,
                region = config.region_name,
                using_custom_endpoint = bool(config.endpoint_url)
            )
            
            instance = S3Connector(
                bucket_name = config.bucket_name,
                access_key = config.access_key_id,
                secret_key = config.secret_access_key,
                region = config.region_name,
                endpoint_url = config.endpoint_url
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
        engine_type = db_type or settings.DB_TYPE.upper()
        
        logger = structlog.get_logger("switchboard.factory").bind(
            provider = engine_type
        )

        if engine_type == "DUCKDB":
            
            path = kwargs.get("connection_string") or settings.DUCKDB_PATH
            
            logger.info(
                "[Factory Database] Using DuckDB. Data will be stored in a local DuckDB file.",
                connection_string = path
            )
            
            instance = DuckDBConnector(path)
            
        elif engine_type == "POSTGRES":
            
            logger.info("[Factory Database] Initializing database provider")
            
            # Border Guard: Validate incoming arguments using our schema
            config = PostgresConfig(
                connection_string = kwargs.get("connection_string") or settings.POSTGRES_URL
            )
            
            logger.info(
                "[Factory Database] Database provider configuration validated", 
                connection_string = config.connection_string
            )
            
            instance = PostgresConnector(config.connection_string)
            
        elif engine_type == "CLICKHOUSE":
            
            logger.info("[Factory Database] Initializing database provider")

            # Border Guard: Validate incoming arguments using our schema
            config = ClickHouseConfig(
                host = kwargs.get("host") or settings.CLICKHOUSE_HOST,
                port = kwargs.get("port") or settings.CLICKHOUSE_PORT,
                user = kwargs.get("username") or settings.CLICKHOUSE_USER,
                password = kwargs.get("password") or settings.CLICKHOUSE_PASSWORD
            )
            
            logger.info(
                "[Factory Database] Database provider configuration validated", 
                host = config.host,
                port = config.port,
                user = config.user
            )

            instance = ClickHouseConnector(
                host = config.host,
                port = config.port,
                user = config.user,
                password = config.password
            )
            
        elif engine_type == "BIGQUERY":
            
            logger.info("[Factory Database] Initializing database provider")
            
            # Border Guard: Validate incoming arguments using our schema
            config = BigQueryConfig(
                project_id = kwargs.get("project_id") or settings.BQ_PROJECT_ID,
                dataset_id = kwargs.get("dataset_id") or settings.BQ_DATASET_ID,
                credentials_path = kwargs.get("credentials_path") or settings.GOOGLE_APPLICATION_CREDENTIALS
            )
            
            logger.info(
                "[Factory Database] Database provider configuration validated", 
                project_id = config.project_id,
                dataset_id = config.dataset_id
            )

            instance = BigQueryConnector(
                project_id = config.project_id,
                dataset_id = config.dataset_id,
                credentials_path = config.credentials_path
            )
        
        elif engine_type == "REDSHIFT":
            logger.info("Initializing database provider", provider = "REDSHIFT")
            
            # Run parameters through our Pydantic border checkpoint
            config = RedshiftConfig(
                host = kwargs.get("host") or settings.REDSHIFT_HOST,
                port = kwargs.get("port") or settings.REDSHIFT_PORT,
                database = kwargs.get("database") or settings.REDSHIFT_DATABASE,
                username = kwargs.get("username") or settings.REDSHIFT_USER,
                password = kwargs.get("password") or settings.REDSHIFT_PASSWORD
            )
            
            logger.info(
                "Database provider configuration validated",
                provider = "REDSHIFT",
                target_host = config.host,
                target_db = config.database
            )
            
            instance = RedshiftConnector(
                host = config.host,
                port = config.port,
                database = config.database,
                username = config.username,
                password = config.password
            )
        
        else:
            raise ValueError(f"Unsupported DB type: {engine_type}")

        cls._db_instances[name] = instance
        return instance