from __future__ import annotations
import time

from .loggers import BaseLogger
from .analyzers import BaseAnalyzer

class Database:

    def __init__(
            self,
            logger: BaseLogger,
            analyser: BaseAnalyzer,
    ) -> None:
        self.logger: BaseLogger = logger
        self.analyser: BaseAnalyzer = analyser


    def get_db_data(
            self,
            connect_data: dict,
            file_path: str,
            time_waiting: int,
    ) -> bool:
        """
        Запускаем логирование запросов
        Возвращаем успешно ли прошло логирование
        """
        if self.logger.connect(**connect_data):
            self.logger.start_logging(file_path=file_path)
            time.sleep(time_waiting)
            self.logger.stop_logging()
            return True
        return False
    
    
    def analyze(self, file_path: str) -> dict[str, int]:
        return self.analyser.analyze(file_path=file_path)
