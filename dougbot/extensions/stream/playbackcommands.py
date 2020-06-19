import os

import discord
from discord.ext import commands


class VideoStream(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def stream(self, ctx):
        pth = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
        print(pth)
        f = discord.File(pth)
        await ctx.send(file=f)


def setup(bot):
    bot.add_cog(VideoStream(bot))
