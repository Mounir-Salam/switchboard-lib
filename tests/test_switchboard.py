from switchboard.factory import Switchboard
import os

def test_full_switchboard_flow():
    # 1. Get the tools from the factory
    storage = Switchboard.get_storage()
    db = Switchboard.get_db()
    
    # 2. Test Storage
    storage.write("switch_test.txt", "Switchboard is alive!")
    
    # 3. Test Database
    db.execute("CREATE TABLE IF NOT EXISTS flow_test (id INTEGER, status TEXT)")
    db.execute("INSERT INTO flow_test VALUES (1, 'Integrated')")
    
    res = db.get_as_dataframe("SELECT * FROM flow_test")
    assert res.iloc[0]['status'] == 'Integrated'
    print("\n✅ Switchboard successfully routed to LocalFS and DuckDB!")

if __name__ == "__main__":
    test_full_switchboard_flow()