from abc import ABC, abstractmethod
from typing import Any

class StorageProvider(ABC):
    @abstractmethod
    def read(self, path: str) -> bytes:
        pass

    @abstractmethod
    def write(self, path: str, data: Any) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Safely closes any underlying network sockets or client sessions."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()