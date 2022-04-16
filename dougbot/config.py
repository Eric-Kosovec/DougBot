import hashlib
import os
from configparser import ConfigParser
from types import SimpleNamespace

import cachetools

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTENSIONS_DIR = os.path.join(ROOT_DIR, 'dougbot', 'extensions')
RESOURCES_DIR = os.path.join(ROOT_DIR, 'resources')
RESOURCES_MAIN_PACKAGE_DIR = os.path.join(RESOURCES_DIR, 'dougbot')
EXTENSION_RESOURCES_DIR = os.path.join(RESOURCES_MAIN_PACKAGE_DIR, 'extensions')

_CONFIG_PATH = os.path.join(RESOURCES_DIR, 'config')
_CONFIG_FILENAME = 'config.ini'
_TEST_CONFIG_FILENAME = 'test_config.ini'


@cachetools.cached(cache={})
def get_configuration():
    config = os.path.join(_CONFIG_PATH, _CONFIG_FILENAME)
    test_config = os.path.join(_CONFIG_PATH, _TEST_CONFIG_FILENAME)

    config_parser = ConfigParser()
    config_parser.read([config, test_config])

    command_prefix = config_parser.get('Commands', 'prefix')
    admin_role_id = int(config_parser.get('Permissions', 'admin_role_id'))
    logging_channel_id = int(config_parser.get('Channels', 'logging_channel_id'))

    db_url = os.getenv(config_parser.get('Environment', 'db_url_name'))
    db_api_key = os.getenv(config_parser.get('Environment', 'db_api_key_name'))

    token = os.getenv(config_parser.get('Environment', 'token_name'))

    if os.path.exists(test_config):  # For test config only settings - These ones should NEVER exist in regular config
        test_config_parser = ConfigParser()
        test_config_parser.read(test_config)
        if token is None:
            token = test_config_parser.get('Environment', 'token', fallback=None)

    config_namespace = SimpleNamespace()
    config_namespace.command_prefix = command_prefix
    config_namespace.admin_role_id = admin_role_id
    config_namespace.logging_channel_id = logging_channel_id
    config_namespace.token = token
    config_namespace.db_url = db_url
    config_namespace.db_api_key = db_api_key

    return config_namespace
