import pytest
import pandas as pd
from switchboard.factory import Switchboard

def test_db_write_and_read():
    # ---------------------------------------------------------
    # 1. Test the DEFAULT Database (Uses your .env settings)
    # ---------------------------------------------------------
    db_default = Switchboard.get_db(name="default")
    
    # Create sample data
    df = pd.DataFrame({"id": [1, 2], "val": ["A", "B"]})
    
    print("\n##################### Writing to DEFAULT database...")
    db_default.write_table(df, "test_table")
    
    print("##################### DEFAULT Database write successful. Now reading back...")
    result_df = db_default.get_as_dataframe("SELECT * FROM test_table")
    
    assert len(result_df) == 2
    assert result_df["val"].iloc[0] == "A"
    print("##################### DEFAULT Database read verified.")
    
    # Clean up default
    db_default.execute("DROP TABLE IF EXISTS test_table")

    # ---------------------------------------------------------
    # 2. Test a SECONDARY, Named Database on the fly
    #    (Proves the Registry can maintain isolated connections)
    # ---------------------------------------------------------
    print("\n##################### Spinning up SECONDARY isolated database...")
    db_secondary = Switchboard.get_db(
        name="isolated_analytics", 
        db_type="DUCKDB", 
        connection_string="./data/secondary_test.db"
    )
    
    # Create different sample data
    df_secondary = pd.DataFrame({"id": [100], "val": ["Z"]})
    
    print("##################### Writing to SECONDARY database...")
    db_secondary.write_table(df_secondary, "analytics_table")
    
    # Verify data exists in secondary
    result_secondary = db_secondary.get_as_dataframe("SELECT * FROM analytics_table")
    assert len(result_secondary) == 1
    assert result_secondary["val"].iloc[0] == "Z"
    print("##################### SECONDARY Database read verified.")

    # ---------------------------------------------------------
    # 3. Cross-Isolation Check 
    #    (Proves db_default cannot see db_secondary's tables)
    # ---------------------------------------------------------
    print("\n##################### Verifying database isolation...")
    try:
        # This should fail if they are properly isolated, because 'analytics_table' 
        # only exists in the secondary database file.
        db_default.get_as_dataframe("SELECT * FROM analytics_table")
        pytest.fail("Isolation breached! Default database could see secondary tables.")
    except Exception:
        print("##################### Isolation verified! Default database cannot see secondary data.")

    # Clean up secondary
    db_secondary.execute("DROP TABLE IF EXISTS analytics_table")

if __name__ == "__main__":
    test_db_write_and_read()