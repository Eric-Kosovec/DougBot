from discord.ext import commands

from dougbot.extensions.common.annotations.admincheck import admin_command


class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def clearlog(self, ctx):
        log_channel = await self.bot.log_channel()
        if log_channel is not None:
            await log_channel.purge(check=lambda m: m.author.id == ctx.me.id, bulk=False)
            await ctx.message.delete()

    @commands.command()
    async def hi(self, ctx):
        await ctx.send('Hello?')


def setup(bot):
    bot.add_cog(Debug(bot))
