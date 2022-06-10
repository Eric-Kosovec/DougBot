from supabase import client
from supabase.client import Client

from dougbot import config


def connect() -> Client:
    configs = config.get_configuration()
    return client.create_client(configs.db_url, configs.db_api_key)


async def check_connection():
    db_client = None
    try:
        db_client = connect()
        db_client.storage().list_buckets()
        return True
    except Exception:
        return False
    finally:
        if db_client:
            db_client.auth.close()
