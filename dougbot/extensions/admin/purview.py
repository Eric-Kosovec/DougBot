from discord.ext import commands

from dougbot.extensions.common.admin_check import admin_command


class Purview(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def hi(self, ctx):
        await ctx.send('Hello?')

    @commands.command()
    @admin_command()
    async def view_kv(self, ctx, module):
        pass

    @commands.command()
    @admin_command()
    async def view_kvs(self, ctx, module):
        pass


def setup(bot):
    bot.add_cog(Purview(bot))
