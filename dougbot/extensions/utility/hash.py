import hashlib

from nextcord.ext import commands
from nextcord.ext.commands import Context

from dougbot.common.messaging import reactions
from dougbot.core.bot import DougBot
from dougbot.extensions.common import webutils


class Hash(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    async def hash(self, ctx: Context, algorithm: str, *, text: str = None):
        if text:
            bytes_to_hash = bytes(text, encoding='utf-8')
        elif len(ctx.message.attachments) > 0:
            bytes_to_hash = await webutils.url_get(ctx.message.attachments[0].url)
        else:
            await reactions.confusion(ctx.message, 'Nothing provided to hash', delete_text_after=5)
            return

        try:
            await ctx.send(hashlib.new(algorithm, bytes_to_hash).hexdigest())
        except Exception:
            await reactions.confusion(ctx.message, 'Bad hash algorithm', delete_text_after=5)


def setup(bot: DougBot):
    bot.add_cog(Hash(bot))
