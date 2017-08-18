class CommandConflictError(Exception):
    def __init__(self, existing_plugin, attempt_command):
        super().__init__("Command '%s' conflicts with existing command in %s." % (attempt_command, existing_plugin))
