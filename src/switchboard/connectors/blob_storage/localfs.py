import shutil
import structlog
from switchboard.base.storage import StorageProvider
from pathlib import Path
from typing import Any

class LocalFSConnector(StorageProvider):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents = True, exist_ok = True)
        
        self.logger = structlog.get_logger("switchboard.localfs").bind(
            provider = "LOCAL",
        )

    def read(self, path: str) -> bytes:
        full_path = self.base_path / path
        
        self.logger.info(f"Fetching data from path: {full_path}")
        
        return full_path.read_bytes()

    def write(self, path: str, data: Any) -> None:
        full_path = self.base_path / path
        full_path.parent.mkdir(parents = True, exist_ok = True)
        
        self.logger.info(f"Writing data to path: {full_path}")
        
        if isinstance(data, str):
            full_path.write_text(data, encoding="utf-8")
        elif isinstance(data, bytes):
            full_path.write_bytes(data)
        else:
            encoded_data = str(data).encode("utf-8")
            full_path.write_bytes(encoded_data)
    
    def close(self) -> None:
        """Placeholder for interface consistency. LocalFS doesn't maintain persistent connections."""
        pass