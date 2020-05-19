from discord.ext import commands

from dougbot.extensions.util.admin_check import admin_command


class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def clearlog(self, ctx):
        log_channel = await self.bot.log_channel()
        if log_channel is not None:
            await log_channel.purge(check=lambda m: m.author.id == ctx.me.id, bulk=False)

    @commands.command()
    @admin_command()
    async def panic(self, _):
        raise ValueError('BAD VALUE')


def setup(bot):
    bot.add_cog(Debug(bot))
