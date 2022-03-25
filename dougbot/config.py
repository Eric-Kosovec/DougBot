import hashlib
import os
from configparser import ConfigParser
from types import SimpleNamespace

import cachetools

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTENSIONS_DIR = os.path.join(ROOT_DIR, 'dougbot', 'extensions')
RESOURCES_DIR = os.path.join(ROOT_DIR, 'resources')
EXTENSION_RESOURCES_DIR = os.path.join(RESOURCES_DIR, 'dougbot', 'extensions')

_CONFIG_PATH = os.path.join(ROOT_DIR, 'resources', 'config')
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

    db_hostname = config_parser.get('Database', 'hostname')
    db_port = int(config_parser.get('Database', 'port'))
    db_username = config_parser.get('Database', 'username')

    token = os.getenv(config_parser.get('Environment', 'token_name'))

    db_password = None
    if os.path.exists(test_config):  # For test config only settings - These ones should NEVER exist in regular config
        test_config_parser = ConfigParser()
        test_config_parser.read(test_config)
        db_password = test_config_parser.get('Database', 'password', fallback=None)
        if token is None:
            token = test_config_parser.get('Environment', 'token', fallback=None)

    if db_password is None:
        sha256_hash = hashlib.new('sha256')
        sha256_hash.update(token.encode('utf-8'))
        db_password = sha256_hash.hexdigest()

    config_namespace = SimpleNamespace()
    config_namespace.command_prefix = command_prefix
    config_namespace.admin_role_id = admin_role_id
    config_namespace.logging_channel_id = logging_channel_id
    config_namespace.db_hostname = db_hostname
    config_namespace.db_port = db_port
    config_namespace.db_username = db_username
    config_namespace.db_password = db_password
    config_namespace.token = token

    return config_namespace
