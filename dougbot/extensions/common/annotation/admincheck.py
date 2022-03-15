import nextcord
from nextcord.ext import commands
from nextcord.user import User

from dougbot import config


def admin_command():
    def predicate(ctx):
        admin_role_id = config.get_configuration().admin_role_id
        return ctx.me.id == ctx.author.id or \
            (not isinstance(ctx.author, User) and nextcord.utils.find(lambda r: r.id == admin_role_id, ctx.author.roles))

    return commands.check(predicate)
