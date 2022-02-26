import os
import shutil

import nextcord
from nextcord.ext import commands

from dougbot.common.messaging import reactions
from dougbot.common.messaging.message_utils import split_message
from dougbot.core.bot import DougBot
from dougbot.extensions.common import fileutils
from dougbot.extensions.common import webutils
from dougbot.extensions.common.annotations.admincheck import admin_command


class ResourceManager(commands.Cog):

    # TODO MORE GENERAL MANAGER

    def __init__(self, bot: DougBot):
        self.bot = bot
        self._root = os.path.join(self.bot.ROOT_DIR, 'resources', 'dougbot')

    @commands.command()
    @admin_command()
    async def ls(self, ctx, path: str = '.'):
        files = await self.ls_noadmin(path)
        for message in split_message('\n'.join(files)):
            await ctx.send(message)

    async def ls_noadmin(self, path: str = '.'):
        target = fileutils.PathBuilder(self._root) \
            .join(path) \
            .build()

        files = os.listdir(target)
        files.sort()
        return files

    @commands.command()
    @admin_command()
    async def rm(self, ctx, path: str):
        await self.rm_noadmin(path)
        await reactions.confirmation(ctx.message)

    async def rm_noadmin(self, path: str):
        target = fileutils.PathBuilder(self._root) \
            .join(path) \
            .build()

        if os.path.isfile(target):
            os.remove(target)
        else:
            os.removedirs(target)

    @commands.command()
    @admin_command()
    async def rmall(self, ctx, directory: str):
        await self.rmall_noadmin(directory)
        await reactions.confirmation(ctx.message)

    async def rmall_noadmin(self, directory: str):
        target = fileutils.PathBuilder(self._root) \
            .join(directory) \
            .build()

        if os.path.isdir(target):
            shutil.rmtree(target)

    @commands.command()
    @admin_command()
    async def get(self, ctx, path: str):
        target = fileutils.PathBuilder(self._root) \
            .join(path) \
            .build()

        if os.path.isfile(target):
            await ctx.send(file=nextcord.File(target))
        else:
            await reactions.confusion(ctx.message, f'{target} is not a file')

    @commands.command()
    @admin_command()
    async def mv(self, ctx, source: str, dest: str):
        source_path = fileutils.PathBuilder(self._root) \
            .join(source) \
            .build()

        dest_path = fileutils.PathBuilder(self._root) \
            .join(dest) \
            .build()

        os.makedirs(dest_path, exist_ok=True)
        os.rename(source_path, dest_path)

        await reactions.confirmation(ctx.message)

    @commands.command()
    @admin_command()
    async def rename(self, ctx, source: str, dest: str):
        await self.mv(ctx, source, dest)

    @commands.command()
    @admin_command()
    async def mkdir(self, ctx, directory: str):
        target = fileutils.PathBuilder(self._root) \
            .join(directory) \
            .build()

        os.mkdir(target)

        await reactions.confirmation(ctx.message)

    @commands.command()
    @admin_command()
    async def mkfile(self, ctx, path: str):
        if len(ctx.message.attachments) == 0:
            await reactions.confusion(ctx.message, 'No attachments given')
            return

        target = fileutils.PathBuilder(self._root) \
            .join(path) \
            .build()

        url = ctx.message.attachments[0].url
        file = await webutils.download_file(url)
        with open(target, 'wb') as fd:
            shutil.copyfileobj(file.raw, fd)

        await reactions.confirmation(ctx.message)


def setup(bot):
    bot.add_cog(ResourceManager(bot))
