from discord.ext.commands.help import HelpCommand


class CustomHelpCommand(HelpCommand):

    def __init__(self):
        super().__init__()
        self._is_bot_help = False
        self._ctx = None

    async def prepare_help_command(self, ctx, command=None):
        self._is_bot_help = command is None
        self._ctx = ctx

    def get_destination(self):
        if self._is_bot_help:
            self._is_bot_help = False
            return self._ctx.author.dm_channel
        else:
            return super().get_destination()
