from discord.ext import commands

from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotations.admincheck import admin_command


class Debug(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def clearlog(self, ctx):
        log_channel = await self.bot.log_channel()
        if log_channel is not None:
            await log_channel.purge(check=lambda m: m.author.id == ctx.me.id, bulk=False)
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(Debug(bot))
