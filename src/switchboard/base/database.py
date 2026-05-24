from abc import ABC, abstractmethod
from typing import Any
import pandas as pd

class DatabaseProvider(ABC):
    @abstractmethod
    def execute(self, query: str) -> Any:
        pass

    @abstractmethod
    def get_as_dataframe(self, query: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def write_table(self, df: pd.DataFrame, table_name: str, mode: str = "replace"):
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Safely closes any underlying network sockets or client sessions."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()