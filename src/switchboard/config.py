from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    
    # Switches
    STORAGE_TYPE: Literal["LOCAL"] = "LOCAL"
    DB_TYPE: Literal["DUCKDB", "POSTGRES"] = "DUCKDB"
    
    # Specific settings
    LOCAL_STORAGE_PATH: str = "data/storage"
    DUCKDB_PATH: str = "data/main.db"
    POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # Environment variable settings
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()