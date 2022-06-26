from nextcord.ext import commands
from nextcord.ext.commands import Context

from dougbot.core.bot import DougBot


class Links(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    async def sdt(self, ctx: Context):
        await ctx.send('https://cytu.be/r/SadDoug')


def setup(bot):
    bot.add_cog(Links(bot))
