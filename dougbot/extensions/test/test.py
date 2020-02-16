from discord.ext import commands


class Test(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        kvstore = await self.bot.get_kvstore()
        kvstore.insert('Test', 'TEST_ME', '5')
        kvstore.insert('Test', 'TEST_ME2', '6')


def setup(bot):
    bot.add_cog(Test(bot))
