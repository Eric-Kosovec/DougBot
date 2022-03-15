from mysql import connector

from dougbot import config


def connect(database=None):
    configs = config.get_configuration()
    return connector.connect(
        host=f'{configs.db_hostname}:{configs.db_port}',
        database=database,
        user=configs.db_username,
        password=configs.db_password)
