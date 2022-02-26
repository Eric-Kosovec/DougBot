from nextcord.ext import commands

from dougbot.core.bot import DougBot


class Bank(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        # Calling the bank from a different extension: bank = self.bot.get_cog('Bank')


def setup(bot):
    bot.add_cog(Bank(bot))
