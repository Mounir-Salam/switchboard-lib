import pytest
import logging
from unittest.mock import patch
from tenacity import RetryError
from switchboard.utils.resilience import cloud_retry

# Configure logging visibility so we can watch the retry warning triggers in real time
logging.basicConfig(level = logging.WARNING)

# Let's create a dummy tracker class to simulate a real connection medium
class FlakyService:
    def __init__(self):
        self.attempts = 0

    @cloud_retry(max_attempts = 3)
    def fetch_data(self, fail_until_attempt: int):
        self.attempts += 1
        print(f"\n[Execution Track] Inside fetch_data. Attempt number: {self.attempts}")
        
        if self.attempts < fail_until_attempt:
            print(f"💥 Simulating a transient ConnectionError on attempt {self.attempts}!")
            raise ConnectionError("Remote server socket closed unexpectedly.")
            
        print("🎉 Success! Connection stable, returning data stream.")
        return b"recovered_payload_bytes"


def test_successful_recovery_on_retry():
    print("\n--- Starting Resilience Test 1: Self-Healing Stream ---")
    service = FlakyService()
    
    # We tell it to fail on attempts 1 and 2, but succeed on attempt 3.
    # Our decorator allows up to 3 attempts, so this should recover smoothly!
    data = service.fetch_data(fail_until_attempt = 3)
    
    assert data == b"recovered_payload_bytes"
    assert service.attempts == 3
    print("✅ System successfully self-healed after 2 network failures.")


def test_hard_failure_when_max_attempts_exceeded():
    print("\n--- Starting Resilience Test 2: Catastrophic Crash Target ---")
    service = FlakyService()
    
    # We tell it to fail until attempt 5. 
    # Since our max_attempts is capped at 3, it should eventually give up and raise the error.
    with pytest.raises(ConnectionError):
        service.fetch_data(fail_until_attempt = 5)
        
    assert service.attempts == 3
    print("✅ System correctly threw a hard error when network limits were exceeded.")


if __name__ == "__main__":
    test_successful_recovery_on_retry()
    test_hard_failure_when_max_attempts_exceeded()