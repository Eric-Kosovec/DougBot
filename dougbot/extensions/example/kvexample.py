from discord.ext import commands


class KVExample(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.kv = self.bot.kv_store()

    async def random_command(self, _):
        self.kv['THIS MUST BE A STRING'] = 'THIS CAN BE ANYTHING, NOT NECESSARY A STRING'
        self.kv['TEST'] = 5
        x = self.kv['TEST']
        _ = x


def setup(bot):
    bot.add_cog(KVExample(bot))
