import sqlite3
from sqlite3 import Error


class DougBotDB:
    _DOUGBOT_DB_PATH = 'dougbot.db'

    def __init__(self):
        self.connection = self._create_connection()
        return

    def _create_connection(self):
        try:
            connection = sqlite3.connect(self._DOUGBOT_DB_PATH)
            return connection
        except Error as e:
            print(e)
            return None

    def get_connection(self):
        return self.connection

    def close(self):
        self.connection.commit()
        self.connection.close()
