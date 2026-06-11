import structlog
import boto3
from switchboard.base.storage import StorageProvider
from switchboard.utils.resilience import cloud_retry

class S3Connector(StorageProvider):
    def __init__(self, bucket_name: str, access_key: str, secret_key: str, region: str = "us-east-1", endpoint_url: str = None):
        self.bucket_name = bucket_name
        
        self.logger = structlog.get_logger("switchboard.s3").bind(
            bucket = self.bucket_name,
            provider = "S3"
        )

        # 🔌 Conditional Router: If endpoint_url is passed (LocalStack), we use it.
        # If it's None, Boto3 automatically connects directly to the real AWS Cloud.
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            region_name = region,
            endpoint_url = endpoint_url
        )
        
        # Determine if we are running in a local sandbox mode based on the endpoint URL
        self.is_local = endpoint_url is not None and "localhost" in endpoint_url
        
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """
        Validates target bucket availability.
        - Sandbox Mode (LocalStack): Automatically creates the bucket if missing.
        - Production Mode (Real AWS): Strictly errors out if infrastructure isn't provisioned.
        """
        try:
            self.s3_client.head_bucket(Bucket = self.bucket_name)
        except Exception:
            if self.is_local:
                self.logger.info("Local sandbox bucket not found. Initializing mock infrastructure", target_bucket = self.bucket_name)
                try:
                    self.s3_client.create_bucket(Bucket = self.bucket_name)
                except Exception as e:
                    self.logger.error("Failed to automatically initialize local bucket", error = str(e))
                    raise
            else:
                self.logger.error(
                    "Target bucket does not exist. Production infrastructure must be provisioned via Terraform or AWS Console.",
                    target_bucket = self.bucket_name
                )
                raise FileNotFoundError(
                    f"The AWS S3 bucket '{self.bucket_name}' could not be reached or does not exist. "
                    f"Please verify your cloud infrastructure setup."
                )

    @cloud_retry(max_attempts = 4)
    def read(self, path: str) -> bytes:
        self.logger.info("Fetching data from remote path", remote_path = path)
        
        try:
            response = self.s3_client.get_object(Bucket = self.bucket_name, Key = path)
            # 🤝 Pillar 4: Safe stream context tracking releases network handles instantly
            with response["Body"] as stream:
                return stream.read()
        except self.s3_client.exceptions.NoSuchKey:
            self.logger.error("Object read failed: key does not exist", remote_path = path)
            raise FileNotFoundError(f"The object '{path}' does not exist in bucket '{self.bucket_name}'.")

    @cloud_retry(max_attempts = 4)
    def write(self, path: str, data: any) -> None:
        self.logger.info("Writing data stream to remote path", remote_path = path)
        
        body = data if isinstance(data, bytes) else str(data).encode("utf-8")
        self.s3_client.put_object(Bucket = self.bucket_name, Key = path, Body = body)

    def close(self) -> None:
        """Safely tears down active boto3 core transport thread pools."""
        if hasattr(self, "s3_client") and self.s3_client is not None:
            self.logger.info("Closing active AWS S3 boto3 client connections")
            try:
                self.s3_client.close()
            except Exception as e:
                self.logger.warning("Error encountered while closing boto3 transport layer", error = str(e))