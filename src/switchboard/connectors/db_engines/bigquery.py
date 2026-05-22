import os
import pandas as pd
from google.cloud import bigquery
from switchboard.base.database import DatabaseProvider
from switchboard.utils.resilience import cloud_retry

class BigQueryConnector(DatabaseProvider):
    def __init__(self, project_id: str, dataset_id: str, credentials_path: str = None):
        self.project_id = project_id
        self.dataset_id = dataset_id
        
        job_config = bigquery.QueryJobConfig(default_dataset=f"{self.project_id}.{self.dataset_id}")
        
        # Set the auth environment variable if a specific path is passed
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
        self.client = bigquery.Client(project=self.project_id, default_query_job_config=job_config)
        
        # 🛑 Dataset creation disabled by design.
        # We assume the infrastructure (datasets) is managed externally.
        # self._ensure_dataset_exists()

    """
    # Commented out: Leave infrastructure management to the UI or Terraform
    def _ensure_dataset_exists(self):
        dataset_ref = bigquery.DatasetReference(self.project_id, self.dataset_id)
        try:
            self.client.get_dataset(dataset_ref)
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            self.client.create_dataset(dataset, timeout=30)
    """

    def execute(self, query: str):
        query_job = self.client.query(query)
        query_job.result()  # Wait for the statement to finish

    @cloud_retry(max_attempts=4)
    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        query_job = self.client.query(query)
        return query_job.to_dataframe()

    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        # BigQuery targets tables using project.dataset.table layout
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        write_disposition = (
            bigquery.WriteDisposition.WRITE_TRUNCATE 
            if mode == "replace" 
            else bigquery.WriteDisposition.WRITE_APPEND
        )
        
        job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
        
        # 2. Route the execution based on safety constraints
        if mode == "replace":
            # TRUNCATE operations are completely idempotent. 
            # If it fails halfway and retries, it just wipes the canvas and starts over.
            self._execute_upload_with_retry(df, table_ref, job_config)
        else:
            # APPEND operations are NOT safe to blindly retry.
            # We execute it exactly once. If it fails, we let it crash so the user can investigate.
            self._execute_upload_raw(df, table_ref, job_config)

    @cloud_retry(max_attempts=4)
    def _execute_upload_with_retry(self, df, table_ref, job_config):
        """Internal retriable method helper."""
        self._execute_upload_raw(df, table_ref, job_config)

    def _execute_upload_raw(self, df, table_ref, job_config):
        """Single raw attempt execution path."""
        job = self.client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()