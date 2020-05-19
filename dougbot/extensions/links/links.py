from discord.ext import commands


class Links(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sdt(self, ctx):
        await ctx.send('https://cytu.be/r/SadDoug')
        '''kvstore = await self.bot.kvstore()
        try:
            kvstore.insert('LINK', 'https://cytu.be/r/SadDoug')
        except Exception as e:
            print(f'ERROR AS {e}')'''
        '''v = kvstore.get('LINK')
        print(f'GOT: {v}')
        c = kvstore.contains('LINK')
        print(c)
        for k, v in kvstore:
            print(f'{k}, {v}')
        kvstore.remove('LINK', 'https://cytu.be/r/SadDoug')
        c = kvstore.contains('LINK')
        print(c)'''

    @commands.command()
    async def git(self, ctx):
        await ctx.send(self.bot.config.source_code)


def setup(bot):
    bot.add_cog(Links(bot))
