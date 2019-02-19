from Lib.configparser import ConfigParser


class Config:

    def __init__(self, config_file):
        self._config_file = config_file

        config_parser = ConfigParser()
        config_parser.read(self._config_file)

        self.token = config_parser.get('Credentials', 'Token')
        self.command_prefix = config_parser.get('Chat', 'CommandPrefix')
        self.owner = config_parser.get('Permissions', 'OwnerID')
        self.description = config_parser.get('General', 'Description')
        self.source_code = config_parser.get('General', 'SourceCode')
        self.avatar_url = config_parser.get('General', 'AvatarURL')



