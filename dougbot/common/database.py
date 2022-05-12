from supabase import client
from supabase.client import Client

from dougbot import config
from dougbot.common.logevent import LogEvent


def connect() -> Client:
    configs = config.get_configuration()
    return client.create_client(configs.db_url, configs.db_api_key)


async def check_connection():
    db_client = None
    try:
        db_client = connect()
        db_client.storage().list_buckets()
        return True
    except Exception as e:
        LogEvent(__file__) \
            .message('Database down') \
            .exception(e) \
            .error()
        return False
    finally:
        if db_client is not None:
            db_client.auth.close()
