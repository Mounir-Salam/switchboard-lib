from switchboard.utils.logging import configure_logging
from switchboard.factory import Switchboard

def run_sample_pipeline(label: str):
    print(f"\n--- Running Pipeline Sample with format: {label} ---")
    
    # Simulate an operations workflow calling our hardened connector layer
    gcs = Switchboard.get_storage(name = f"log_test_{label}", storage_type = "GCS")
    
    try:
        gcs.write("logs/heartbeat.txt", "system_active_status")
        gcs.read("logs/heartbeat.txt")
    except Exception:
        # Ignoring concrete cloud network execution errors since we are only verifying log output style
        pass

if __name__ == "__main__":
    # 1. Test Local Development Logging Output (Human-Friendly Text formatting)
    configure_logging(production_mode = False)
    run_sample_pipeline(label = "LOCAL_DEV")
    
    # 2. Test Production Environment Output (Machine-Parsable Structured JSON formatting)
    configure_logging(production_mode = True)
    run_sample_pipeline(label = "PRODUCTION_CLOUD")