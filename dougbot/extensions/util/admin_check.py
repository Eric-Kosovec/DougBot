from discord.ext import commands


def admin_command():
    def predicate(ctx):
        return next(filter(lambda role: role.name == 'Admin', ctx.message.author.roles), None) is not None

    return commands.check(predicate)

