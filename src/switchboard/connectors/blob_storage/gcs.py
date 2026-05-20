import os
from google.cloud import storage
from switchboard.base.storage import StorageProvider

class GCSConnector(StorageProvider):
    def __init__(self, bucket_name: str, credentials_path: str = None):
        self.bucket_name = bucket_name
        
        # If an explicit credentials path is passed via kwargs, register it
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
        self.client = storage.Client()
        
        # Following our architectural pattern: assume the bucket infrastructure is managed externally via Terraform or Console UI.
        self.bucket = self.client.bucket(self.bucket_name)

    def read(self, path: str) -> bytes:
        blob = self.bucket.blob(path)
        if not blob.exists():
            raise FileNotFoundError(f"The object '{path}' does not exist in bucket '{self.bucket_name}'.")
        return blob.download_as_bytes()

    def write(self, path: str, data: any) -> None:
        blob = self.bucket.blob(path)
        
        # Convert inputs to bytes if they aren't already string or raw bytes
        if isinstance(data, bytes):
            blob.upload_from_string(data, content_type="application/octet-stream")
        elif isinstance(data, str):
            blob.upload_from_string(data.encode("utf-8"), content_type="text/plain")
        else:
            blob.upload_from_string(str(data).encode("utf-8"), content_type="text/plain")