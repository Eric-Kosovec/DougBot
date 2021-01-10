import os

import discord
from discord.ext import commands


class Storage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._file_dir = os.path.join(self.bot.ROOT_DIR, 'resources', 'files')
        #if not os.path.isdir(self._file_dir):


    @commands.command(aliases=['image'])
    async def file(self, ctx, image: str):
        path = await self._find_file(image)
        if path is None:
            await self.bot.confusion(ctx.message)
        else:
            await ctx.channel.send(file=discord.File(path))

    @commands.command(aliases=['images'])
    async def files(self, ctx):
        enter = ''
        message = 'Files:\n'

        files = os.listdir(self._file_dir) if os.path.exists(self._file_dir) else []
        for file in files:
            last_dot = file.rfind('.')
            if last_dot >= 0:
                message += enter + file
                enter = '\n'

        await ctx.send(message)

    async def _find_file(self, filename):
        if filename is None or '..' in filename or not os.path.exists(self._file_dir):
            return None

        for file in os.listdir(self._file_dir):
            if file == filename:
                return os.path.join(self._file_dir, file)

        return None


def setup(bot):
    bot.add_cog(Storage(bot))
