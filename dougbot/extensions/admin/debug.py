from nextcord.ext import commands

from dougbot import config
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
        await ctx.message.delete(delay=3)

    @clear.command()
    @admin_command()
    async def debug(self, ctx):
        debug_channel = await channelutils.channel_name_like(ctx.message.guild, self._DEBUG_CHANNEL_NAME)
        await channelutils.clear_channel(debug_channel, limit=self._DELETE_LIMIT)
        await ctx.message.delete(delay=3)


def setup(bot):
    bot.add_cog(Debug(bot))
