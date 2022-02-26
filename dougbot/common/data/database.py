import os
import sqlite3


class Database:

    def __init__(self, database_file):
        self._database_file = database_file
        self._create_file(self._database_file)
        self._connection = None

    def open(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self._database_file)

    def close(self):
        if self._connection is not None:
            self._connection.commit()
            self._connection.close()
            self._connection = None

    def execute(self, sql, parameters=None):
        cursor = self._connection.cursor()

        if parameters is None:
            cursor.execute(sql)
        elif isinstance(parameters, list):
            cursor.executemany(sql, parameters)
        else:
            cursor.execute(sql, parameters)

        self._connection.commit()
        return iter(cursor.fetchall())

    def list_tables(self):
        cursor = self._connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return iter(cursor.fetchall())

    def has_table(self, table):
        cursor = self._connection.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        return cursor.fetchone() is not None

    @staticmethod
    def _create_file(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as _:
            pass