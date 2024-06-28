from __future__ import annotations
from collections.abc import Callable
import re
from re import Pattern
from fuzzywuzzy import fuzz

from .base import BaseAnalyzer

class MysqlAnalyzer(BaseAnalyzer):

    FULL_MATCH = 1
    PARTIAL_MATCH = 2

    pattern_query: Pattern = re.compile(r"^.*Query(.+)")
    pattern_connect: Pattern = re.compile(r"^.*Connect(.+)")


    def __init__(self, type: int = FULL_MATCH) -> None:
        self.type: int = type
    
    def set_type(self, type: int) -> None:
        self.type = type
    
    def set_ratio_percent(self, ratio_percent: int) -> None:
        self.ratio_percent = ratio_percent


    def analyze(self,  file_path: str) -> dict[str, int]:
        """
        Анализирует файл и возвращает результаты.
        
        Если `type` равен `FULL_MATCH`, то анализирует только полные соответствия.
        В противном случае, анализирует частичные соответствия.
        
        Аргументы:
            file_path (str): Путь к файлу, который требуется проанализировать.
            
        Возвращает:
            dict[str, int]: Словарь, где ключи - запросы из файла,
            а значения - количество соответствий запросов.
        """

        if self.type == self.FULL_MATCH:
            result = self.process_file(
                file_path=file_path,
                process_line_func=self._get_full_match_queryes,
            )
        else:
            result = self.process_file(
                file_path=file_path,
                process_line_func=self._get_partial_match_queryes,
                ratio_percent=self.ratio_percent,
            )
        return self._sort(result)
    

    def _get_full_match_queryes(
        self,
        line: str,
        result: dict[str, int]
    ) -> dict[str, int]:
        """
        Добавляет запрос в словарь. Если запрос уже есть в словаре,
        то увеличивает значение на 1.
        
        Аргументы:
            line (str): Запрос для добавления в словарь.
            result (dict[str, int]): Словарь, в который добавляется запрос.
        
        Возвращает:
            dict[str, int]: Отредактированный словарь.
        """
        if line not in result:
            result[line] = 1
        else:
            result[line] += 1
        return result

    
    def _get_partial_match_queryes(
        self,
        line: str,
        result: dict[str, int],
        ratio_percent: int = 80
    ) -> dict[str, int]:
        """
        Добавляет запрос в словарь. Если запрос имеет сходство с уже имеющимся в словаре,
        то имеющемуся увеличивает значение на 1.
        
        Аргументы:
            line (str): Запрос для добавления в словарь.
            result (dict[str, int]): Словарь, в который добавляется запрос.
            ratio_percent (int): Процент сходства запросов. По умолчанию = 80
        
        Возвращает:
            dict[str, int]: Отредактированный словарь.
        """
        added = False
        for key in result.keys():
            if fuzz.ratio(line, key) > ratio_percent:
                result[key] += 1
                added = True
                break
        if not added:
            result[line] = 1
        return result
    
    
    def process_file(self,
            file_path: str,
            process_line_func: Callable[..., dict[str, int]],
            **kwargs
        ) -> dict[str, int]:
        """
        Анализирует файл логов обрабатывая каждую строку переданной функцией process_line_func
        
        Аргументы:
            file_path (str): Путь к файлу, который требуется проанализировать.
            process_line_func (Callable): Функция, которая будет применяться к каждой строке файла.
            
        Возвращает:
            dict: Результаты обработки файла
        """
        result = {}
        with open(file_path, "r") as f:
            for line in f:
                l = line.strip()
                res = self.pattern_query.findall(l)
                if res:
                    result = process_line_func(res[0].strip(), result, **kwargs)
        return result
