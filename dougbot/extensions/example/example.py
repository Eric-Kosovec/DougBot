from discord.ext import commands

from dougbot.core.bot import DougBot


class Example(commands.Cog):

    def __init__(self, bot: DougBot):  # Doing the bot: DougBot
        self.bot = bot


def setup(bot):
    bot.add_cog(Example(bot))
