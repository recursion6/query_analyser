from mysql.connector import errorcode
import mysql.connector

from .base import BaseLogger

class MysqlLogger(BaseLogger):
    running = False

    def connect(
            self,
            username: str,
            password: str,
            hostname: str,
            database_name: str
        ) -> bool:
        """ Пытаемся подключиться к базе данных """
        print("Пытаемся подключиться к базе данных \n")
        try:
            self.cnx = mysql.connector.connect(
                user=username,
                password=password,
                host=hostname,
                database=database_name
            )
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Доступ запрещен, пользователь или пароль неверны")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("База данных не существует")
            else:
                print(err)
            return False


    def start_logging(self, file_path: str):
        """ Запускаем логирование запросов """
        print("Запускаем логирование запросов \n")
        self.running = True
        cursor = self.cnx.cursor()
        cursor.execute('SET global log_output = "FILE";')
        cursor.execute("SET global general_log_file=%(path)s;", {"path": file_path})
        cursor.execute("SET global general_log = 1;")
        self.cnx.commit()
        cursor.close()


    def stop_logging(self):
        """ Останавливаем логирование запросов """
        print("Останавливаем логирование запросов \n")
        cursor = self.cnx.cursor()
        query = "SET global general_log = 0;"
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        self.running = False
        print("Остановили \n")

    
    def __del__(self):
        """ Закрываем соединение с базой данных """
        if self.running:
            self.stop_logging()
        if hasattr(self, 'cnx'):
            self.cnx.close()
            print("Закрываем соединение \n")
