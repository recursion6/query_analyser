from __future__ import annotations
from abc import (
    ABC,
    abstractmethod,
)

class BaseAnalyzer(ABC):
    
    @abstractmethod
    def analyze(self,  file_path: str) -> dict[str, int]:
        """Анализируем данные"""
        pass
    

    def _sort(self, data: dict[str, int]) -> dict[str, int]:
        """Сортируем данные в обратном порядке"""
        return dict(
            sorted(
                data.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )