from discord.ext import commands
from discord.user import User


def voice_command():
    def predicate(ctx):
        return not isinstance(ctx.message.author, User) and ctx.message.author.voice is not None
    return commands.check(predicate)
