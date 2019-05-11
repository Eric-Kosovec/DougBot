import os

import discord
from discord.ext import commands


class FileManager(commands.Cog):
    FILE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    FILE_DIR = os.path.join(FILE_DIR, 'res', 'files')

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['getimg'])
    async def getfile(self, ctx, image: str):
        path = await self._find_file(image)
        if path is None:
            await self.bot.confusion(ctx.message)
        else:
            await ctx.channel.send(file=discord.File(path))

    @commands.command(aliases=['images'])
    async def listfiles(self, ctx):
        enter = ''
        message = 'Files:\n'

        for file in os.listdir(self.FILE_DIR):
            last_dot = file.rfind('.')
            if last_dot >= 0:
                message += enter + file
                enter = '\n'

        await ctx.send(message)

    async def _find_file(self, filename):
        if filename is None:
            return None

        if '..' in filename:
            return None

        for file in os.listdir(self.FILE_DIR):
            if file == filename:
                return os.path.join(self.FILE_DIR, file)

        return None


def setup(bot):
    bot.add_cog(FileManager(bot))
