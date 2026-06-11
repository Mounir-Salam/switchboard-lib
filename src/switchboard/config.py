from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Literal
from typing import Optional

class Settings(BaseSettings):
    
    # Switches
    STORAGE_TYPE: Literal["LOCAL", "MINIO", "S3", "GCS"] = "LOCAL"
    DB_TYPE: Literal["DUCKDB", "POSTGRES", "CLICKHOUSE", "BIGQUERY", "REDSHIFT"] = "DUCKDB"
    
    @field_validator("STORAGE_TYPE", mode = "before")
    @classmethod
    def uppercase_storage_type(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value
    
    @field_validator("DB_TYPE", mode = "before")
    @classmethod
    def uppercase_db_type(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value
    
    # Local settings
    LOCAL_STORAGE_PATH: str = "data/storage"
    
    # MinIO Settings
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "switchboard-bucket"
    
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID: str = "mock_sandbox_key"
    AWS_SECRET_ACCESS_KEY: str = "mock_sandbox_secret"
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: str = "switchboard-local-lake"
    AWS_ENDPOINT_URL: Optional[str] = None  # Crucial for routing to Docker!
    
    # DuckDB settings
    DUCKDB_PATH: str = "data/main.db"
    
    # PostgreSQL settings
    POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # ClickHouse settings
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    
    # BigQuery & GCS Settings
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None  # Path to your service_account.json
    BQ_PROJECT_ID: str | None = None
    BQ_DATASET_ID: str | None = None
    GCS_BUCKET_NAME: str | None = None
    
    # AWS Redshift settings
    REDSHIFT_HOST: str = "localhost"
    REDSHIFT_PORT: int = 5439
    REDSHIFT_DATABASE: str = "dev"
    REDSHIFT_USER: str = "awsuser"
    REDSHIFT_PASSWORD: str = "password"
    
    # Environment variable settings
    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")

settings = Settings()