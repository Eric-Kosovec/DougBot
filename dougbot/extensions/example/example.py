from nextcord.ext import commands
from nextcord.ext.commands import Context

from dougbot.core.bot import DougBot


class Example(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    async def example_command(self, ctx: Context):
        pass


def setup(bot: DougBot):
    bot.add_cog(Example(bot))


def teardown(bot: DougBot):
    _ = bot
