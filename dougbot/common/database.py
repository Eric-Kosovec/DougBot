from mysql.connector import connection
from mysql.connector.types import Tuple

from dougbot import config

def connect() -> connection:
    configs = config.get_configuration()
    return connection.MySQLConnection(user=configs.username, password=configs.password, host=configs.host, database=configs.database)

def connect_specific(username: str, password: str, host: str, database_name: str) -> connection:
    configs = config.get_configuration()
    return connection.MySQLConnection(user=username, password=password, host=host, database=database_name)

def mysql_select(conn: connection, query: str) -> Tuple:
    cursor = conn.cursor()
    cursor.execute(query)
    result_set = cursor.fetchall()
    return result_set

def mysql_insert(conn: connection, statement: str) -> int:
    cursor = conn.cursor()
    cursor.execute(statement)
    conn.commit()
    return cursor.rowcount()

def mysql_delete(conn: connection, statement: str) -> int:
    cursor = conn.cursor()
    cursor.execute(statement)
    conn.commit()
    return cursor.rowcount()

def mysql_update(conn: connection, statement: str) -> int:
    cursor = conn.cursor()
    cursor.execute(statement)
    conn.commit()
    return cursor.rowcount()