import asyncio

from nextcord.ext import commands

from dougbot.core.bot import DougBot
from dougbot.extensions.common import channelutils
from dougbot.extensions.common.annotations.admincheck import admin_command


class Debug(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def clearlog(self, ctx):
        log_channel = await self.bot.log_channel()
        await self._clear_channel(ctx, log_channel)

    @commands.command()
    @admin_command()
    async def cleardebug(self, ctx):
        debug_channel = await channelutils.channel_containing_name(ctx.message.guild, 'doug-debug')
        await self._clear_channel(ctx, debug_channel)

    @staticmethod
    async def _clear_channel(ctx, channel):
        if channel is not None:
            await channel.purge(limit=10000, check=lambda m: not m.pinned, bulk=True)
            if ctx.message.channel.id != channel.id:
                await asyncio.sleep(3)
                await ctx.message.delete()


def setup(bot):
    bot.add_cog(Debug(bot))
