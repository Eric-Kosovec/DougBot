from nextcord.ext import commands

from dougbot.core.bot import DougBot
from dougbot.extensions.common import channelutils
from dougbot.extensions.common.annotation.admincheck import admin_command


class Debug(commands.Cog):

    _DELETE_DELAY = 3
    _DELETE_LIMIT = 10000
    _DEBUG_CHANNEL_NAME = 'doug-debug'

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @admin_command()
    async def clear(self, ctx):
        await ctx.send("'clear log' or 'clear debug'")
        await ctx.message.delete()

    @clear.command()
    @admin_command()
    async def log(self, ctx):
        await channelutils.clear_channel(ctx, await self.bot.log_channel(), limit=self._DELETE_LIMIT, delay=self._DELETE_DELAY)

    @clear.command()
    @admin_command()
    async def debug(self, ctx):
        debug_channel = await channelutils.channel_containing_name(ctx.message.guild, self._DEBUG_CHANNEL_NAME)
        await channelutils.clear_channel(ctx, debug_channel, limit=self._DELETE_LIMIT, delay=self._DELETE_DELAY)


def setup(bot):
    bot.add_cog(Debug(bot))
