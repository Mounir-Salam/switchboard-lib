import shutil
from switchboard.base.storage import StorageProvider
from pathlib import Path
from typing import Any

class LocalFSConnector(StorageProvider):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def read(self, path: str) -> bytes:
        full_path = self.base_path / path
        return full_path.read_bytes()

    def write(self, path: str, data: Any) -> None:
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, str):
            full_path.write_text(data)
        else:
            full_path.write_bytes(data)
        print(f"✅ File written to {full_path}")