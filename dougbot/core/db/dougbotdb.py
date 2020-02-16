import os
import sqlite3
from sqlite3 import Error


class DougBotDB:
    DB_NAME = 'dougbot.db'
    DB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    DB_PATH = os.path.join(DB_PATH, 'db', DB_NAME)

    def __init__(self):
        self.connection = self._create_connection()

    # TODO CATCH SQL EXCEPTIONS

    def insert_into(self, table, values, where=None):
        if table is None or values is None:
            return
        cursor = self._get_cursor()
        if where is None:
            cursor.execute('INSERT INTO ? VALUES (?)', (table, values,))
        else:
            cursor.execute('INSERT INTO ? VALUES (?) WHERE ?', (table, values, where,))
        self.connection.commit()

    def select_from(self, columns, table, where=None):
        if columns is None or table is None:
            return
        cursor = self._get_cursor()
        if where is None:
            cursor.execute('SELECT ? FROM ?', (columns, table,))
        else:
            cursor.execute('SELECT ? FROM ? WHERE ?', (columns, table, where,))
        for row in cursor:
            yield row

    def delete_from(self, table, where):
        if table is None or where is None:
            return
        cursor = self._get_cursor()
        cursor.execute('DELETE FROM ? WHERE ?', (table, where,))
        self.connection.commit()

    def create_table(self, table_name, schema):
        if table_name is None or schema is None:
            return
        cursor = self._get_cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS ? (?)', (table_name, schema,))
        self.connection.commit()

    def has_row(self, columns, table, where=None):
        if table is None or columns is None or table is None:
            return
        cursor = self._get_cursor()
        if where is None:
            cursor.execute('SELECT ? FROM ?', (columns, table,))
        else:
            cursor.execute('SELECT ? FROM ? WHERE ?', (columns, table, where,))
        return cursor.fetchone() is not None

    def has_table(self, table_name):
        cursor = self._get_cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='?'", (table_name,))
        return cursor.fetchone() is not None

    def get_connection(self):
        if self.connection is None:
            self.connection = self._create_connection()
        return self.connection

    def close(self):
        self.connection.commit()
        self.connection.close()
        self.connection = None

    def _create_connection(self):
        try:
            connection = sqlite3.connect(self.DB_PATH)
            return connection
        except Error as e:  # TODO MAKE BETTER ERROR REPORTING
            print(e)
            return None

    def _get_cursor(self):
        if self.connection is None:
            self.connection = self._create_connection()
        return self.connection.cursor()
