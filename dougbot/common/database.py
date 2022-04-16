from supabase.client import create_client, Client

from dougbot import config


def connect() -> Client:
    configs = config.get_configuration()
    return create_client(configs.db_url, configs.db_api_key)
