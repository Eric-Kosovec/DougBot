from dougbot.common import database

from nextcord.ext import commands
from dougbot.core.bot import DougBot

class TestDB(commands.Cog):
    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    async def testSelect(self, ctx):

        conn = database.connect()
        result = database.mysql_select(conn, 'SELECT User,Host FROM mysql.user;')

        await ctx.send("I found this many: " + str(len(result)))

def setup(bot):
    bot.add_cog(TestDB(bot))
