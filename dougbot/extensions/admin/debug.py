from nextcord.ext import commands

from dougbot import config
from dougbot.common.messaging import reactions
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotation.admincheck import admin_command, mod_command


class Debug(commands.Cog):
    _DELETE_LIMIT = 1000

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.group()
    async def clear(self, _):
        pass

    @clear.command()
    @admin_command()
    async def log(self, ctx):
        log_channel = await self.bot.fetch_channel(config.get_configuration().logging_channel_id)
        await self._clear_channel(log_channel)
        await reactions.confirmation(ctx.message, delete_message_after=3)

    @clear.command()
    @admin_command()
    async def debug(self, ctx):
        debug_channel = await self.bot.fetch_channel(config.get_configuration().debug_channel_id)
        await self._clear_channel(debug_channel)
        await reactions.confirmation(ctx.message, delete_message_after=3)

    async def _clear_channel(self, channel):
        await channel.purge(limit=self._DELETE_LIMIT, check=lambda m: not m.pinned, bulk=True)


def setup(bot):
    bot.add_cog(Debug(bot))
