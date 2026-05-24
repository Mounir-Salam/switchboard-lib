import structlog
import boto3
from io import BytesIO
from switchboard.base.storage import StorageProvider

class MinioConnector(StorageProvider):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            endpoint_url = endpoint,
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            # MinIO doesn't use regions like AWS, but boto3 requires a placeholder
            region_name = "us-east-1" 
        )
        self._ensure_bucket_exists()
        
        self.logger = structlog.get_logger("switchboard.minio").bind(
            bucket = self.bucket_name,
            provider = "MINIO"
        )

    def _ensure_bucket_exists(self):
        """Helper to create the bucket if it's missing"""
        try:
            self.s3_client.head_bucket(Bucket = self.bucket_name)
        except:
            self.s3_client.create_bucket(Bucket = self.bucket_name)

    def read(self, path: str) -> bytes:
        self.logger.info(f"Fetching data from path: {path}")
        
        response = self.s3_client.get_object(Bucket = self.bucket_name, Key = path)
        with response["Body"] as stream:
            return stream.read()

    def write(self, path: str, data: any) -> None:
        self.logger.info(f"Writing data to path: {path}")
        
        # Boto3 expects bytes or a file-like object
        body = data if isinstance(data, bytes) else str(data).encode("utf-8")
        self.s3_client.put_object(Bucket = self.bucket_name, Key = path, Body = body)

    def close(self) -> None:
        """Safely tears down the active boto3 client network infrastructure."""
        if hasattr(self, "s3_client") and self.s3_client is not None:
            self.logger.info("Closing active MinIO client sessions")
            try:
                # Boto3 clients expose a native close function directly
                self.s3_client.close()
            except Exception as e:
                self.logger.warning("Error encountered while closing MinIO client", error=str(e))