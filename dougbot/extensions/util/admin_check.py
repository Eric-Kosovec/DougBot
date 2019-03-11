from discord.ext import commands


def admin_command():
    def predicate(ctx):
        return (ctx.bot.user.id == ctx.message.author.id or
                next(filter(lambda role: role.name == 'Admin', ctx.message.author.roles), None) is not None)

    return commands.check(predicate)
