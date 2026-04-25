from abc import ABC, abstractmethod
from typing import Any

class StorageProvider(ABC):
    @abstractmethod
    def read(self, path: str) -> bytes:
        pass

    @abstractmethod
    def write(self, path: str, data: Any) -> None:
        pass