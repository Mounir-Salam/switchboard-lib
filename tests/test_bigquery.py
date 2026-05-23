import pytest
import pandas as pd
from switchboard.factory import Switchboard

def test_bigquery_pipeline():
    # Create distinct sample datasets
    df_dev = pd.DataFrame({"id": [1, 2], "environment": ["dev_A", "dev_B"]})
    df_sec = pd.DataFrame({"id": [100], "environment": ["secondary_Z"]})

    # -------------------------------------------------------------------------
    # 1. Test DEFAULT Connection (Targets switchboard_dev via .env)
    # -------------------------------------------------------------------------
    print("\n🚀 Connecting to DEFAULT BigQuery Dataset...")
    bq_default = Switchboard.get_db(name = "default_bq", db_type = "BIGQUERY")
    
    print("Writing table to 'switchboard_dev'...")
    bq_default.write_table(df_dev, "bq_test_table", mode = "replace")
    
    print("Reading back from 'switchboard_dev'...")
    result_dev = bq_default.get_as_dataframe("SELECT * FROM bq_test_table")
    
    assert len(result_dev) == 2
    assert result_dev["environment"].iloc[0] == "dev_A"
    print("✅ DEFAULT BigQuery connection verified.")

    # -------------------------------------------------------------------------
    # 2. Test SECONDARY Connection (Targets secondary_test via custom kwargs)
    # -------------------------------------------------------------------------
    print("\n🚀 Connecting to SECONDARY BigQuery Dataset via kwargs...")
    # We pass dataset_id explicitly to override the .env value
    bq_secondary = Switchboard.get_db(
        name = "secondary_bq",
        db_type = "BIGQUERY",
        project_id = "de-zoomcamp-484617",
        dataset_id = "secondary_test",
        credentials_path = "./secrets/bg_gcs.json"
    )
    
    print("Writing table to 'secondary_test'...")
    bq_secondary.write_table(df_sec, "bq_analytics_table", mode = "replace")
    
    print("Reading back from 'secondary_test'...")
    result_sec = bq_secondary.get_as_dataframe("SELECT * FROM bq_analytics_table")
    
    assert len(result_sec) == 1
    assert result_sec["environment"].iloc[0] == "secondary_Z"
    print("✅ SECONDARY BigQuery connection verified.")

    # -------------------------------------------------------------------------
    # 3. Cross-Isolation Check
    # -------------------------------------------------------------------------
    print("\n🛡️ Verifying BigQuery Dataset isolation...")
    try:
        # Default connection (switchboard_dev) shouldn't see the secondary table
        bq_default.get_as_dataframe("SELECT * FROM bq_analytics_table")
        pytest.fail("Isolation breached! Default connection could read secondary table.")
    except Exception:
        print("✅ Isolation verified! Default connection cannot see secondary dataset tables.")

    # -------------------------------------------------------------------------
    # 4. Clean up tables
    # -------------------------------------------------------------------------
    print("\n🧹 Cleaning up BigQuery tables...")
    bq_default.execute("DROP TABLE IF EXISTS bq_test_table")
    bq_secondary.execute("DROP TABLE IF EXISTS bq_analytics_table")
    print("✅ Cleanup complete.")

if __name__ == "__main__":
    test_bigquery_pipeline()