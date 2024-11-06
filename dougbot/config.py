import os
import sys
from configparser import ConfigParser
from types import SimpleNamespace

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(ROOT_DIR, 'dougbot', 'core')
EXTENSIONS_DIR = os.path.join(ROOT_DIR, 'dougbot', 'extensions')
RESOURCES_DIR = os.path.join(ROOT_DIR, 'resources')
RESOURCES_MAIN_PACKAGE_DIR = os.path.join(RESOURCES_DIR, 'dougbot')
EXTENSION_RESOURCES_DIR = os.path.join(RESOURCES_MAIN_PACKAGE_DIR, 'extensions')

_CONFIG_PATH = os.path.join(RESOURCES_DIR, 'config')
_CONFIG_FILENAME = 'config.ini'
_DEV_CONFIG_FILENAME = 'dev_config.ini'

_CONFIGURATION = None


def get_configuration():
    global _CONFIGURATION

    if _CONFIGURATION is not None:
        return _CONFIGURATION

    try:
        config = os.path.join(_CONFIG_PATH, _CONFIG_FILENAME)
        dev_config = os.path.join(_CONFIG_PATH, _DEV_CONFIG_FILENAME)

        config_parser = ConfigParser()
        config_parser.read([config, dev_config])

        config_namespace = SimpleNamespace()

        # Commands
        config_namespace.command_prefix = config_parser.get('Commands', 'prefix')

        # Channels
        config_namespace.debug_channel_id = int(config_parser.get('Channels', 'debug_channel_id'))
        config_namespace.logging_channel_id = int(config_parser.get('Channels', 'logging_channel_id'))

        # Environment
        config_namespace.username = os.getenv(config_parser.get('Environment', 'username'))
        config_namespace.password = os.getenv(config_parser.get('Environment', 'password'))
        config_namespace.host = os.getenv(config_parser.get('Environment', 'host'))
        config_namespace.database = os.getenv(config_parser.get('Environment', 'database'))
        config_namespace.token = os.getenv(config_parser.get('Environment', 'token_name'))

        # Debug Env - Do this so you don't have to set environment vars. Just edit config.ini with login info
        # config_namespace.username = config_parser.get('Environment', 'username')
        # config_namespace.password = config_parser.get('Environment', 'password')
        # config_namespace.host = config_parser.get('Environment', 'host')
        # config_namespace.database = config_parser.get('Environment', 'database')

        # Logging
        config_namespace.log_to_console = _str_to_bool(config_parser.get('Logging', 'log_to_console', fallback='False'))
        config_namespace.fatal_log_size = int(float(config_parser.get('Logging', 'fatal_log_size', fallback='0')))

        # Meta
        config_namespace.is_dev_bot = os.path.exists(dev_config)

        # Permissions
        config_namespace.admin_role_id = int(config_parser.get('Permissions', 'admin_role_id'))
        config_namespace.mod_role_id = int(config_parser.get('Permissions', 'mod_role_id'))

        # Resilience
        config_namespace.run_attempt_cooldown_secs = int(
            config_parser.get('Resilience', 'run_attempt_cooldown_secs', fallback='5'))

        _CONFIGURATION = config_namespace

        return config_namespace
    except Exception as e:
        print(f'FATAL: Bot failed to start, invalid config: {e}', file=sys.stderr)


def _str_to_bool(string: str):
    return string is not None and string.lower() in ['1', 't', 'true']
