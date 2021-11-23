from configparser import ConfigParser


class Config:

    def __init__(self, token_file, bot_config, server_config):
        bot_config_parser = ConfigParser()
        bot_config_parser.read(bot_config)

        server_config_parser = ConfigParser()
        server_config_parser.read(server_config)

        self.token = self._read_token(token_file)
        self.command_prefix = bot_config_parser.get('Commands', 'Prefix')
        self.admin_role_id = int(server_config_parser.get('Permissions', 'AdminRoleID'))
        self.logging_channel_id = int(server_config_parser.get('Channels', 'LoggingChannelID'))

    @staticmethod
    def _read_token(token_file):
        with open(token_file, 'r') as fd:
            return fd.read()
