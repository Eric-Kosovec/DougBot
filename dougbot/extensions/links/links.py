from nextcord.ext import commands


class Links(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sdt(self, ctx):
        await ctx.send('https://cytu.be/r/SadDoug')

    @commands.command()
    async def bingo(self, ctx):
        await ctx.send('http://saddoug.rf.gd/')


def setup(bot):
    bot.add_cog(Links(bot))
