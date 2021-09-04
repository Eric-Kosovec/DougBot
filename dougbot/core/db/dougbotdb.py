import os
import sqlite3


class DougBotDB:

    def __init__(self, path):
        self._path = path
        self._create_if_not_exists(path)
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
        try:
            if not self.valid_input(table):
                raise ValueError('Invalid table name')
            next(self.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
            return True
        except StopIteration:
            return False

    def open(self):
        return self._get_connection()

    def close(self):
        if self._connection is not None:
            self._connection.commit()
            self._connection.close()
            self._connection = None

    @staticmethod
    def valid_input(text):
        return str.isidentifier(text)

    def _get_connection(self):
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    def _create_connection(self):
        return sqlite3.connect(self._path)

    def _get_cursor(self):
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection.cursor()

    @staticmethod
    def _create_if_not_exists(path):
        if path is not None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as _:
                pass
