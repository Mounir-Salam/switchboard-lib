import pandas as pd
import io
from switchboard.factory import Switchboard
from switchboard.utils.logging import configure_logging

def test_storage_to_database_pipeline():
    configure_logging()
    
    # 1. Setup the Switchboard
    storage = Switchboard.get_storage() # Will be Minio based on .env
    db = Switchboard.get_db()           # Will be Postgres based on .env

    # 2. Simulate an incoming file in MinIO
    raw_csv_data = "id,sample_name,count\n1,HG001,500\n2,HG002,750"
    storage.write("raw/samples.csv", raw_csv_data)
    print("✅ Uploaded raw file to MinIO")

    # 3. Read back from Storage (Extract)
    content = storage.read("raw/samples.csv")
    
    # 4. Process with Pandas (Transform)
    df = pd.read_csv(io.BytesIO(content))
    df['count_plus_bonus'] = df['count'] + 100
    
    # 5. Write to Postgres (Load)
    db.write_table(df, "processed_samples", mode = "replace")
    print("✅ Loaded transformed data into Postgres")

    # 6. Verify the result
    result = db.get_as_dataframe("SELECT * FROM processed_samples")
    assert len(result) == 2
    assert result['count_plus_bonus'].iloc[0] == 600
    print("✅ E2E Pipeline Verified!")

if __name__ == "__main__":
    test_storage_to_database_pipeline()