from configparser import ConfigParser


class Config:

    def __init__(self, token_file, config_file):
        self._config_file = config_file

        config_parser = ConfigParser()
        config_parser.read(self._config_file)

        self.token = self._read_token(token_file)
        self.command_prefix = config_parser.get('Meta', 'CommandPrefix')
        self.admin_role_id = int(config_parser.get('Permissions', 'AdminRoleID'))
        self.logging_channel_id = int(config_parser.get('Channels', 'LoggingChannelID'))

    @staticmethod
    def _read_token(token_file):
        with open(token_file, 'r') as tfd:
            return tfd.read()
