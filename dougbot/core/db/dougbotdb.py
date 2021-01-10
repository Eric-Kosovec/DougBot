import os
import sqlite3


class DougBotDB:
    DB_NAME = 'dougbot.db'
    DB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    DB_PATH = os.path.join(DB_PATH, 'db', DB_NAME)

    def __init__(self):
        self._connection = self._create_connection()

    def execute(self, sql, parameters=None):
        cursor = self._get_cursor()
        if parameters is not None:
            cursor.execute(sql, parameters)
        else:
            cursor.execute(sql)
        self._get_connection().commit()
        return iter(cursor.fetchall())

    def has_table(self, table):
        cursor = self._get_cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        return cursor.fetchone() is not None

    def open(self):
        return self._get_connection()

    def close(self):
        self._connection.commit()
        self._connection.close()
        self._connection = None

    def _get_connection(self):
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    def _create_connection(self):
        return sqlite3.connect(self.DB_PATH)

    def _get_cursor(self):
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection.cursor()
