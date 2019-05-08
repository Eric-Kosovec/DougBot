from discord.ext import commands


class Link(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sdt(self, ctx):
        await ctx.send('https://cytu.be/r/SadDoug')

    @commands.command()
    async def git(self, ctx):
        await ctx.send(self.bot.config.source_code)


def setup(bot):
    bot.add_cog(Link(bot))
