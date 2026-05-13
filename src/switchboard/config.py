from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    
    # Switches
    STORAGE_TYPE: Literal["LOCAL", "MINIO", "S3"] = "LOCAL"
    DB_TYPE: Literal["DUCKDB", "POSTGRES"] = "DUCKDB"
    
    # Specific settings
    LOCAL_STORAGE_PATH: str = "data/storage"
    DUCKDB_PATH: str = "data/main.db"
    POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # MinIO / S3 Settings
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "switchboard-bucket"
    
    # Environment variable settings
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()