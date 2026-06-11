import pandas as pd
from switchboard.factory import Switchboard
from switchboard.utils.logging import configure_logging

def verify_redshift_pipeline():
    # 1. Turn on beautiful dev-focused structured log formatting
    configure_logging(production_mode=False)
    
    print("🚀 Bootstrapping Switchboard Redshift Lifecycle Verification Engine...")
    
    # 2. Mock up a payload using a Pandas Dataframe
    test_data = {
        "user_id": [101, 102, 103],
        "session_duration_mins": [45.2, 12.8, 118.5],
        "device_type": ["mobile", "desktop", "tablet"]
    }
    df_to_upload = pd.DataFrame(test_data)
    
    # 3. Establish the safe execution context using our framework factory
    with Switchboard.get_db(db_type="REDSHIFT") as db:
        
        # Action A: Clean up any old test tables left behind from previous runs
        print("\n🧹 Cleaning up stale sandbox structures...")
        db.execute("DROP TABLE IF EXISTS public.sandbox_user_metrics;")
        
        # Action B: Write our dataframe down directly to a Redshift table target
        print("\n📥 Streaming batch dataframe into Redshift target table...")
        db.write_table(
            df=df_to_upload, 
            table_name="sandbox_user_metrics", 
            mode="replace"
        )
        
        # Action C: Retrieve that data back out to prove storage accuracy
        print("\n📤 Pulling structured query metrics back into memory...")
        retrieved_df = db.get_as_dataframe(
            query="SELECT * FROM public.sandbox_user_metrics WHERE session_duration_mins > 20;"
        )
        
        # Print results to the screen to inspect rows manually
        print("\n🎯 Query Output Matrix (Filtered Dataframe):")
        print(retrieved_df)
        
        # Quick assertion check to guarantee our pipeline integrity works perfectly
        assert len(retrieved_df) == 2, f"Expected 2 rows, but got {len(retrieved_df)}"
        print("\n✅ Internal dataframe verification checks passed cleanly!")

    print("\n🏁 Context manager exited. Redshift database connection pools completely disposed.")

if __name__ == "__main__":
    verify_redshift_pipeline()