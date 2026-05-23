import pytest
from pydantic import ValidationError
from switchboard.factory import Switchboard

def test_invalid_bigquery_config_blocks_immediately():
    print("\n--- Testing Guardrails ---")
    
    # Intentionally trigger an error by supplying an empty project_id string
    # which violates our schema constraints (min_length = 1)
    with pytest.raises(ValidationError) as excinfo:
        Switchboard.get_db(
            name = "broken_bq",
            db_type = "BIGQUERY",
            project_id = "",  # Empty string!
            dataset_id = "analytics"
        )
    
    print("✅ Guardrail successfully caught invalid input!")
    # Let's print out what Pydantic told us
    print(f"Captured Error Context:\n{excinfo.value}")

if __name__ == "__main__":
    test_invalid_bigquery_config_blocks_immediately()