import os
from concurrent.futures import ThreadPoolExecutor

import discord
from discord.ext import commands

from dougbot.extensions.theater.webserver import WebServer


class Theater(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._webserver = None
        self._threadpool = ThreadPoolExecutor(1)

    @commands.command()
    @commands.guild_only()
    async def theater(self, ctx):
        web_files = os.path.join(os.path.dirname(__file__), 'www')
        if self._webserver is None:
            self._webserver = WebServer('localhost', 8080, web_files)
            self._webserver.run()

        pth = os.path.join(os.path.dirname(__file__), 'www', 'index.html')
        print(pth)
        f = discord.File(pth)
        await ctx.send(file=f)

    @commands.command(aliases=['fin', 'finale'])
    @commands.guild_only()
    async def end_theater(self, ctx):
        _ = ctx
        try:
            if self._webserver is not None and self._webserver.is_running():
                self._webserver.close()
        finally:
            self._webserver = None


def setup(bot):
    bot.add_cog(Theater(bot))
