import pytest
from switchboard.factory import Switchboard

def test_gcs_storage_pipeline():
    # 1. Setup sample data payloads
    payload_dev = "raw_sample_id,sample_name\n1,HG001_gcs"
    payload_sec = "raw_sample_id,sample_name\n100,HG002_gcs_secondary"

    # -------------------------------------------------------------------------
    # 1. Test DEFAULT Connection (Targets switchboard-dev-lake via .env)
    # -------------------------------------------------------------------------
    print("\n🚀 Connecting to DEFAULT GCS Bucket...")
    gcs_default = Switchboard.get_storage(name = "default_gcs", storage_type = "GCS")
    
    print("Writing file to 'switchboard-dev-lake'...")
    gcs_default.write("landing/samples.csv", payload_dev)
    
    print("Reading back from 'switchboard-dev-lake'...")
    result_dev = gcs_default.read("landing/samples.csv")
    
    # decode() converts bytes back into a string for comparison
    assert result_dev.decode("utf-8") == payload_dev
    print("✅ DEFAULT GCS connection verified.")

    # -------------------------------------------------------------------------
    # 2. Test SECONDARY Connection (Targets secondary-test-lake via kwargs)
    # -------------------------------------------------------------------------
    print("\n🚀 Connecting to SECONDARY GCS Bucket via kwargs...")
    # Passing bucket_name as a kwarg dynamically overrides our .env default
    gcs_secondary = Switchboard.get_storage(
        name = "secondary_gcs",
        storage_type = "GCS",
        bucket_name = "de-zoomcamp-484617-secondary-test-lake"
    )
    
    print("Writing file to 'secondary-test-lake'...")
    gcs_secondary.write("landing/isolated_samples.csv", payload_sec)
    
    print("Reading back from 'secondary-test-lake'...")
    result_sec = gcs_secondary.read("landing/isolated_samples.csv")
    
    assert result_sec.decode("utf-8") == payload_sec
    print("✅ SECONDARY GCS connection verified.")

    # -------------------------------------------------------------------------
    # 3. Cross-Isolation Check
    # -------------------------------------------------------------------------
    print("\n🛡️ Verifying GCS Bucket isolation...")
    try:
        # The default connection bucket should not be able to find the file 
        # that we uploaded exclusively to the secondary bucket.
        gcs_default.read("landing/isolated_samples.csv")
        pytest.fail("Isolation breached! Default connection could read from the secondary bucket.")
    except Exception:
        print("✅ Isolation verified! Default connection cannot see secondary bucket files.")

if __name__ == "__main__":
    test_gcs_storage_pipeline()