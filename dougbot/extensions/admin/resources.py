import os

from nextcord.ext import commands

from dougbot.common.messaging import reactions
from dougbot.common.messaging.message_utils import split_message
from dougbot.config import RESOURCES_DIR
from dougbot.core.bot import DougBot
from dougbot.extensions.common import webutils
from dougbot.extensions.common.annotation.admincheck import admin_command
from dougbot.extensions.common.filemanager import FileManager


class Resources(commands.Cog, FileManager):
    _RESOURCES_PATH = os.path.join(RESOURCES_DIR, 'dougbot')

    def __init__(self, bot: DougBot):
        super().__init__(self._RESOURCES_PATH)
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @admin_command()
    async def resources(self, ctx):
        await ctx.send("Resources commands: get, list, make_directory, remove, rename, create")

    @resources.command(name='get')
    @admin_command()
    async def get_file(self, ctx, path: str):
        file = await super().get_file(path)

        if file is None:
            await reactions.confusion(ctx.message, f'{path} is not a file')
        else:
            await ctx.send(file=file)

        await ctx.message.delete(delay=3)

    @resources.command(name='list')
    @admin_command()
    async def list(self, ctx, path: str = None):
        files = await super().list(path)

        for message in split_message('\n'.join(files)):
            await ctx.send(message)

        await ctx.message.delete(delay=3)

    @resources.command(name='mkdir')
    @admin_command()
    async def make_directory(self, ctx, directory):
        await super().make_directory(directory)
        await reactions.confirmation(ctx.message)
        await ctx.message.delete(delay=3)

    @resources.command(name='remove')
    @admin_command()
    async def remove(self, ctx, path: str, force: bool = False):
        await super().remove(path, force)
        await reactions.confirmation(ctx.message)
        await ctx.message.delete(delay=3)

    @resources.command(name='rename')
    @admin_command()
    async def rename(self, ctx, from_path: str, to_path: str):
        await super().rename(from_path, to_path)
        await reactions.confirmation(ctx.message)
        await ctx.message.delete(delay=3)

    @resources.command(name='create')
    @admin_command()
    async def make_file(self, ctx, path: str, url: str = None):
        if url is None and len(ctx.message.attachments) == 0:
            await reactions.confusion(ctx.message, 'No attachments given')
            return

        if not webutils.is_file_url(url):
            await reactions.confusion(ctx.message, 'Not a file url')
            return

        url = ctx.message.attachments[0].url if url is None else url
        file = await webutils.download_file(url)
        await super().make_file(path, file.raw)

        await reactions.confirmation(ctx.message)
        await ctx.message.delete(delay=3)


def setup(bot):
    bot.add_cog(Resources(bot))
