import pytest
import pandas as pd
from switchboard.factory import Switchboard

def test_db_write_and_read():
    # Initialize database
    db = Switchboard.get_db()
    
    # Create sample data
    df = pd.DataFrame({"id": [1, 2], "val": ["A", "B"]})
    
    print("##################### Writing to database...")
    # Write to DuckDB
    db.write_table(df, "test_table")
    
    print("##################### Database write successful. Now reading back...")
    
    # Read back and verify
    result_df = db.get_as_dataframe("SELECT * FROM test_table")
    
    assert len(result_df) == 2
    assert result_df["val"].iloc[0] == "A"
    print("##################### Database read successful.")
    
    # Clean up
    db.execute("DROP TABLE IF EXISTS test_table")
    
if __name__ == "__main__":
    test_db_write_and_read()