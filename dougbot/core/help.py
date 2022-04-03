from nextcord.ext.commands.core import Group
from nextcord.ext.commands.help import MinimalHelpCommand


class CustomHelpCommand(MinimalHelpCommand):

    def __init__(self, **options):
        super().__init__(**options)

    def add_bot_commands_formatting(self, commands, heading):
        if commands is None:
            return

        command_texts = []

        for command in commands:
            if isinstance(command, Group):
                command_texts.append(self._command_group_text(command))
            else:
                command_texts.append(command.name)

        self.paginator.add_line(f'__**{heading}**__')
        self.paginator.add_line(' '.join(command_texts))

    @staticmethod
    def _command_group_text(group: Group):
        command_names = []
        group_commands = [group]

        while len(group_commands) > 0:
            group_command = group_commands.pop(0)
            if group_command.invoke_without_command:
                command_names.append(group_command.qualified_name)

            for subcommand in group_command.walk_commands():
                if isinstance(subcommand, Group):
                    group_commands.append(subcommand)
                else:
                    command_names.append(subcommand.qualified_name)

        command_names.sort()

        return ' '.join([f'`{n}`' for n in command_names])
