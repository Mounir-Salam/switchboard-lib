import os
import structlog
from google.cloud import storage
from switchboard.base.storage import StorageProvider
from switchboard.utils.resilience import cloud_retry

class GCSConnector(StorageProvider):
    def __init__(self, bucket_name: str, credentials_path: str = None):
        self.bucket_name = bucket_name
        
        # If an explicit credentials path is passed via kwargs, register it
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
        
        self.logger = structlog.get_logger("switchboard.gcs").bind(
            bucket=self.bucket_name
        )

    @cloud_retry(max_attempts=4)
    def read(self, path: str) -> bytes:
        self.logger.info(f"Fetching blob from remote path: {path}")
        blob = self.bucket.blob(path)
        if not blob.exists():
            raise FileNotFoundError(f"The object '{path}' does not exist in bucket '{self.bucket_name}'.")
        return blob.download_as_bytes()

    @cloud_retry(max_attempts=4)
    def write(self, path: str, data: any) -> None:
        self.logger.info(f"Streaming upload to remote path: {path}")
        blob = self.bucket.blob(path)
        
        # Convert inputs to bytes if they aren't already string or raw bytes
        if isinstance(data, bytes):
            blob.upload_from_string(data, content_type="application/octet-stream")
        elif isinstance(data, str):
            blob.upload_from_string(data.encode("utf-8"), content_type="text/plain")
        else:
            blob.upload_from_string(str(data).encode("utf-8"), content_type="text/plain")