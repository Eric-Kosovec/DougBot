
class CommandConflictError(Exception):
    def __init__(self, existing_plugin, attempt_command):
        super().__init__(f'Command {attempt_command} conflicts with existing command in {existing_plugin}.')
