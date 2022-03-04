from nextcord.ext import commands
from nextcord.user import User


def voice_command():

    def predicate(ctx):
        return not isinstance(ctx.message.author, User) and ctx.message.author.voice is not None

    return commands.check(predicate)
