import os
from configparser import ConfigParser


class Config:

    def __init__(self, config, test_config):
        config_parser = ConfigParser()
        config_parser.read([config, test_config] if os.path.exists(test_config) else [config])

        self.command_prefix = config_parser.get('Commands', 'prefix')
        self.admin_role_id = int(config_parser.get('Permissions', 'admin_role_id'))
        self.logging_channel_id = int(config_parser.get('Channels', 'logging_channel_id'))

        token = os.getenv(config_parser.get('Environment', 'token_variable_name'))
        if token is None and os.path.exists(test_config):
            test_config_parser = ConfigParser()
            test_config_parser.read(test_config)
            token = config_parser.get('Environment', 'token', fallback=None)
        self.token = token
