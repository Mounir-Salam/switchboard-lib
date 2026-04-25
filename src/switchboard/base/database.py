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