from nextcord.ext import commands

from dougbot.core.bot import DougBot


class KVExample(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        self.kv = self.bot.kv_store()

    @commands.command()
    async def random_command(self, _):
        self.kv['THIS MUST BE A STRING'] = 'THIS CAN BE ANYTHING, NOT NECESSARY A STRING'
        self.kv['TEST'] = 5
        x = self.kv['TEST']
        _ = x


def setup(bot: DougBot):
    bot.add_cog(KVExample(bot))


def teardown(bot: DougBot):
    _ = bot

