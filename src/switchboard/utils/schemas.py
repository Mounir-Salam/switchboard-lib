from typing import Literal, Optional
from pydantic import BaseModel, Field, FilePath

class BigQueryConfig(BaseModel):
    project_id: str = Field(..., min_length = 1, description = "Google Cloud Project ID")
    dataset_id: str = Field(..., min_length = 1, description = "BigQuery Dataset ID")
    credentials_path: Optional[str] = Field(None, description = "Optional path to service_account.json")

class GCSConfig(BaseModel):
    bucket_name: str = Field(..., min_length = 1, description = "Google Cloud Storage bucket name")
    credentials_path: Optional[str] = Field(None, description = "Optional path to service_account.json")

class ClickHouseConfig(BaseModel):
    host: str = Field("localhost", min_length = 1)
    port: int = Field(8123, ge = 1, le = 65535)
    user: str = Field("default")
    password: str = Field("")

class PostgresConfig(BaseModel):
    connection_string: str = Field(..., min_length = 1)

class MinioConfig(BaseModel):
    endpoint: str = Field(..., min_length = 1, description = "MinIO server endpoint URL")
    access_key: str = Field(..., min_length = 1, description = "MinIO access key / username")
    secret_key: str = Field(..., min_length = 1, description = "MinIO secret key / password")
    bucket_name: str = Field(..., min_length = 1, description = "MinIO bucket name")