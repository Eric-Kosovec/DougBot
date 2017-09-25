import os
import sqlite3
from sqlite3 import Error


class DougBotDB:
    DB_NAME = 'dougbot.db'
    DB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DB_PATH = os.path.join(DB_PATH, DB_NAME)

    def __init__(self):
        self.connection = None

    def _create_connection(self):
        try:
            connection = sqlite3.connect(self.DB_PATH)
            return connection
        except Error as e:
            print(e)
            return None

    def has_table(self, table_name):
        # TODO
        return False

    def get_connection(self):
        if self.connection is None:
            self.connection = self._create_connection()
        return self.connection

    def close(self):
        self.connection.commit()
        self.connection.close()
