from discord.ext import commands

from dougbot.core.bot import DougBot
from extensions.common.annotations.admin_check import admin_command
from dougbot.extensions.common.mic_check import voice_command


class Example(commands.Cog):

    def __init__(self, bot: DougBot):  # Doing the 'bot: DougBot' allows the IDE to see the methods within the bot and be able to list them, for ease of use.
        self.bot = bot

    # Some examples of method decorators that can be used.
    @commands.command()  # Defines a command, using the method name as the command name. (Arguments can be supplied to this: see more in the DiscordPy API docs.)
    @commands.guild_only()  # Prevents command from being used in private messages.
    @admin_command()  # Specifies that the command can only be used by people with the admin role.
    @voice_command()  # Specifies command can only be used while user is in a voice channel.
    def example_command(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Example(bot))
