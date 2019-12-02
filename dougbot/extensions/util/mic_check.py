from discord.ext import commands


def voice_command():
    def predicate(ctx):
        return ctx.message.author.voice is not None
    return commands.check(predicate)
