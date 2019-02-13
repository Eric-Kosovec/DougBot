from discord.ext import commands

class Test:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def test(self, ctx):
        await self.bot.say('Got Tested')


def setup(bot):
    if bot is not None:
        bot.add_cog(Test(bot))
