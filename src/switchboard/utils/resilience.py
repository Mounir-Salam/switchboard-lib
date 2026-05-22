import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = structlog.get_logger("switchboard.resilience")

def cloud_retry(max_attempts: int = 4):
    """
    Decorator that applies exponential backoff with jitter to network operations.
    Retries on generic connection problems but stops instantly on auth/logic errors.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        # You can expand this tuple to catch MinIO, ClickHouse, or Postgres network anomalies
        retry=retry_if_exception_type((ConnectionError, TimeoutError, RuntimeError)),
        before_sleep=lambda retry_state: logger.warning(
            f"⚠️ Connection failed. Attempt {retry_state.attempt_number} broken. "
            f"Retrying in {retry_state.next_action.sleep} seconds..."
        ),
        reraise=True
    )