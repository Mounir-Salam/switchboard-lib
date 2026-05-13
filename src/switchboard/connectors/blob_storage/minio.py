import boto3
from io import BytesIO
from switchboard.base.storage import StorageProvider

class MinioConnector(StorageProvider):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.bucket = bucket
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            # MinIO doesn't use regions like AWS, but boto3 requires a placeholder
            region_name="us-east-1" 
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Helper to create the bucket if it's missing (similar to our LocalFS mkdir)."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except:
            self.s3_client.create_bucket(Bucket=self.bucket)

    def read(self, path: str) -> bytes:
        response = self.s3_client.get_object(Bucket=self.bucket, Key=path)
        return response["Body"].read()

    def write(self, path: str, data: any) -> None:
        # Boto3 expects bytes or a file-like object
        body = data if isinstance(data, bytes) else str(data).encode("utf-8")
        self.s3_client.put_object(Bucket=self.bucket, Key=path, Body=body)