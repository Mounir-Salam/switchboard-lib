import pytest
import pandas as pd
from switchboard.connectors.db_engines.duckdb import DuckDBConnector

def test_duckdb_write_and_read():
    # Initialize an in-memory test database
    db = DuckDBConnector(":memory:")
    
    # Create sample data
    df = pd.DataFrame({"id": [1, 2], "val": ["A", "B"]})
    
    # Write to DuckDB
    db.write_table(df, "test_table")
    
    # Read back and verify
    result_df = db.get_as_dataframe("SELECT * FROM test_table")
    
    assert len(result_df) == 2
    assert result_df["val"].iloc[0] == "A"
    print("##################### Database")