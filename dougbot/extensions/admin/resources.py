from dougbot.extensions.common.file.filemanager import FileManager
from nextcord.ext import commands

from dougbot.common.messaging import reactions
from dougbot.common.messaging.message_utils import split_message
from dougbot.config import RESOURCES_MAIN_PACKAGE_DIR
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotation.admincheck import admin_command


class Resources(commands.Cog, FileManager):

    def __init__(self, bot: DougBot):
        super().__init__(RESOURCES_MAIN_PACKAGE_DIR)
        self.bot = bot

    @commands.group()
    @admin_command()
    async def resources(self, _):
        pass

    @resources.command()
    @admin_command()
    async def get(self, ctx, path: str):
        file = await super().get_file(path)

        if file:
            await ctx.send(file=file)
        else:
            await reactions.confusion(ctx.message, f'{path} is not a file', delete_response_after=10)

        await ctx.message.delete(delay=3)

    @resources.command()
    @admin_command()
    async def list(self, ctx, path: str = None):
        files = await super().list(path)

        for message in split_message('\n'.join(files)):
            await ctx.send(message)

        await ctx.message.delete(delay=3)

    @resources.command()
    @admin_command()
    async def mkdir(self, ctx, directory):
        await super().make_directory(directory)
        await reactions.confirmation(ctx.message, delete_message_after=3)

    @resources.command()
    @admin_command()
    async def remove(self, ctx, path: str, force: bool = False):
        await super().remove(path, force)
        await reactions.confirmation(ctx.message, delete_message_after=3)

    @resources.command()
    @admin_command()
    async def rename(self, ctx, from_path: str, to_path: str):
        await super().rename(from_path, to_path)
        await reactions.confirmation(ctx.message, delete_message_after=3)

    @resources.command()
    @admin_command()
    async def create(self, ctx, path: str, url: str = None):
        if url is None and len(ctx.message.attachments) == 0:
            await reactions.confusion(ctx.message, 'No attachments given', delete_message_after=10, delete_response_after=10)
            return

        # TODO FIX
        '''if await webutils.is_file_url(url):
            file = await webutils.url_get(url if url else ctx.message.attachments[0].url)
            await super().make_file(path, file.raw)
            await reactions.confirmation(ctx.message, delete_message_after=3)
        else:
            await reactions.confusion(ctx.message, 'Not a file url', delete_message_after=10, delete_response_after=10)'''


def setup(bot):
    bot.add_cog(Resources(bot))
