from __future__ import annotations
import os
from getpass import getpass
from typing import Tuple, Union
from pwd import getpwuid
from itertools import islice

from .db import Database
from .loggers import MysqlLogger
from .analyzers import MysqlAnalyzer

class App:

    MODE_FULL = 1
    MODE_ANALYZE = 2

    def __init__(self):
        self.db: Database = Database(
            logger=MysqlLogger(),
            analyser=MysqlAnalyzer(type=MysqlAnalyzer.PARTIAL_MATCH),
        )
    

    def run(self):
        """
        Запуск программы
        """
        mode = input("Режим работы(1 - логирование и анализ, 2 - анализ готового файла логов)[1]: ") or "1"
        try:
            mode = int(mode)
        except ValueError:
            mode = self.MODE_FULL

        if mode == self.MODE_FULL:
            self.run_full_mode()
        elif mode == self.MODE_ANALYZE:
            self.run_analyze_mode()
        else:
            print("Неправильный режим работы")
            return

    
    def run_full_mode(self):
        """
        Запуск программы в полном режиме:
        логирование и анализ запросов в базе данных
        """
        connect_data, file_path, time_waiting, analize_type = self.get_params_full()
        success = self.db.get_db_data(connect_data, file_path, time_waiting)

        if not success:
            print("Не удалось подключиться к базе данных")
            return

        print("Создан файл логов запросов \n")

        res = self.run_analyze(file_path)
        if res is not None:
            print(res)

    
    def run_analyze(self, file_path: str) -> Union[dict[str, int], None]:
        """
        Анализирует файл и возвращает результаты. В противном случае выводит сообщение об
        ошибке и возвращает None.
        """
        if not os.access(file_path, os.R_OK):
            print(f"Нет доступа к файлу {file_path} для чтения, не хватает прав")
            return None
        return self.db.analyze(file_path)
       

    def run_analyze_mode(self) -> int:
        """
        Запускает анализ файла логов запросов
        """
        file_path = input("Путь [/home/user/mysql_general.log]: ") or "/home/user/mysql_general.log"
        self.get_analyze_type()
        
        res = self.run_analyze(file_path)
        if res is not None:
            self.print_result(res)
    
    def get_params_full(self) -> Tuple[dict, str, int]:
        """
        Получает параметры для подключения к базе данных и путь к файлу логов.
        для полного режима
        """
        connect_data = {
            "username": input("Имя пользователя [root]: ") or "root",
            "password": getpass("Пароль: ") or "",
            "hostname": input("Хост [127.0.0.1]: ") or "127.0.0.1",
            "database_name": input("База данных [dbname]: ") or "dbname",
        }
        file_path = input("Путь [/var/log/mysql/mysql_general.log]: ") or "/var/log/mysql/mysql_general.log"
        time_waiting = input("Время(е) сбора запросов в секундах [10]: ") or "10"
        time_waiting = int(time_waiting)
        self.get_analyze_type()
        return connect_data, file_path, time_waiting
    
    def print_result(self, result: dict[str, int], count: int = 20):
        """
        Выводит результат анализа запросов.
        
        Аргументы:
            result (dict[str, int]): словарь, содержащий количество вхождений каждого запроса
            count (int): количество выводимых запросов (по умолчанию - 20)
        """
        print("Результат:")
        items = result.items()
        for item in islice(items, count):
            print(f"{item[1]} - {item[0]} \n")

    def get_analyze_type(self) -> int:
        """
        Получает тип анализа и устанавливает его в анализаторе.
        
        Возвращает:
            int: выбранный тип анализа
        """
        analize_type = int(input("Тип анализа (1 - поиск полного совпадания, 2 - поиск похожих строк)[1]: ") or "1")
        self.db.analyser.set_type(analize_type)
        if analize_type == self.db.analyser.PARTIAL_MATCH:
            self.db.analyser.set_ratio_percent(int(input("Процент совпадения [80]: ") or "80"))
        return analize_type
