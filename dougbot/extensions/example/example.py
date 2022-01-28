from nextcord.ext import commands

from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotations.admincheck import admin_command
from dougbot.extensions.common.annotations.miccheck import voice_command


class Example(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    # Some examples of method decorators that can be used.
    @commands.command()  # Defines a command, using the method name as the command name. (Arguments can be supplied to this: see more in the DiscordPy API docs.)
    @commands.guild_only()  # Prevents command from being used in private messages.
    @admin_command()  # Specifies that the command can only be used by people with the admin role.
    @voice_command()  # Specifies command can only be used while user is in a voice channel.
    async def example_command(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Example(bot))


# Cleanup after extension is unloaded
def teardown(bot):
    _ = bot
