from switchboard.factory import Switchboard
from switchboard.utils.logging import configure_logging

def verify_s3_pipeline():
    # Configure logging to look nice and structured in our terminal local run
    configure_logging(production_mode=False)
    
    print("🚀 Initializing Switchboard S3 Context Manager Verification Engine...")
    
    # Fire up the S3 target within a context manager block
    with Switchboard.get_storage(storage_type="S3") as storage:
        # Write test data
        storage.write("sandbox/test_matrix.txt", "payload_verification_success")
        
        # Read back test data
        data = storage.read("sandbox/test_matrix.txt")
        print(f"📥 Content Retrieved successfully: {data.decode('utf-8')}")
        
    print("🏁 Context exited. S3 client transport threads safely closed.")

if __name__ == "__main__":
    verify_s3_pipeline()