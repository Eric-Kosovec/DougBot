from discord.ext import commands


def admin_command():
    def predicate(ctx):
        return (ctx.me.id == ctx.author.id or
                next(filter(lambda role: role.name == 'Admin', ctx.author.roles), None) is not None)
    return commands.check(predicate)
