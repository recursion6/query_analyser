from abc import (
    ABC,
    abstractmethod,
)

class BaseLogger(ABC):
    
    @abstractmethod
    def connect(
        self,
        username: str,
        password: str,
        hostname: str,
        database_name: str
    ) -> bool:
        """Пытаемся подключиться к базе данных"""
        pass


    @abstractmethod
    def start_logging(self, file_path: str):
        """Запускаем логирование запросов"""
        pass


    @abstractmethod
    def stop_logging(self):
        """Останавливаем логирование запросов"""
        pass
