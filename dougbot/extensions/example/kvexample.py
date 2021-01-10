from discord.ext import commands


class KVExample(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.kv = None

    async def random_command(self, ctx):
        # For now, can only get kv store for your own module. Will be able to get kv stores for modules under same package (folder).
        self.kv = self.bot.kv_store()
        self.kv['THIS MUST BE A STRING'] = 'THIS CAN BE ANYTHING, NOT NECESSARY A STRING'
        self.kv['TEST'] = 5
        my_value = self.kv['TEST']


def setup(bot):
    bot.add_cog(KVExample(bot))
