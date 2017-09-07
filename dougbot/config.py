from Lib.configparser import ConfigParser


class Config:

    def __init__(self, config_file):
        self.config_file = config_file

        config_parser = ConfigParser()
        config_parser.read(config_file)

        self.token = config_parser.get('Credentials', 'Token')
        self.command_prefix = config_parser.get('Chat', 'CommandPrefix')
        self.owner = config_parser.get('Permissions', 'OwnerID')
        self.description = config_parser.get('DougBot', 'Description')
        self.source_code = config_parser.get('DougBot', 'SourceCode')
