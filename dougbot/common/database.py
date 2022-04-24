from supabase import client
from supabase.client import Client

from dougbot import config


def connect() -> Client:
    configs = config.get_configuration()
    return client.create_client(configs.db_url, configs.db_api_key)
