from nextcord.ext import commands
from nextcord.user import User


def admin_command():

    def predicate(ctx):
        return (ctx.me.id == ctx.author.id or (not isinstance(ctx.author, User) and
                                               next(filter(lambda role: role.id == ctx.bot.admin_role_id(), ctx.author.roles), None) is not None))

    return commands.check(predicate)
