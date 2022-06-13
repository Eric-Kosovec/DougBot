from nextcord.ext import commands

from dougbot import config
from dougbot.common import database
from dougbot.common.messaging import reactions
from dougbot.core.bot import DougBot
from dougbot.extensions.common import channelutils
from dougbot.extensions.common.annotation.admincheck import admin_command


class Debug(commands.Cog):
    _DEBUG_CHANNEL_NAME = 'doug-debug'

    _DELETE_LIMIT = 1000

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.group()
    @admin_command()
    async def clear(self, _):
        pass

    @clear.command()
    @admin_command()
    async def log(self, ctx):
        log_channel = await self.bot.fetch_channel(config.get_configuration().logging_channel_id)
        await channelutils.clear_channel(log_channel, limit=self._DELETE_LIMIT)
        await reactions.confirmation(ctx.message, delete_message_after=3)

    @clear.command()
    @admin_command()
    async def debug(self, ctx):
        debug_channel = await channelutils.channel_name_like(ctx.message.guild, self._DEBUG_CHANNEL_NAME)
        await channelutils.clear_channel(debug_channel, limit=self._DELETE_LIMIT)
        await reactions.confirmation(ctx.message, delete_message_after=3)

    @commands.command()
    @admin_command()
    async def health(self, ctx):
        one_hundred_emoji = '\U0001F4AF'
        file_cabinet_emoji = '\U0001F5C4'
        red_x_emoji = '\U0000274C'

        database_status_emoji = red_x_emoji
        if await database.check_connection():
            database_status_emoji = file_cabinet_emoji

        await reactions.reaction_response(ctx.message, one_hundred_emoji)
        await reactions.reaction_response(ctx.message, database_status_emoji, delete_message_after=10)


def setup(bot):
    bot.add_cog(Debug(bot))
