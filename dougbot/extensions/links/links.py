from discord.ext import commands


class Link:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sdt')
    async def theater_link(self):
        await self.bot.say('https://cytu.be/r/SadDoug')

    @commands.command(name='git')
    async def github_link(self):
        await self.bot.say(self.bot.config.source_code)


def setup(bot):
    bot.add_cog(Link(bot))
