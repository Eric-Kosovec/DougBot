import discord.user
from discord.ext import commands


def admin_command():
    def predicate(ctx):
        # Returns true if Bot itself or user is not in a private message and user has the admin role for the channel.
        return (ctx.me.id == ctx.author.id or (not isinstance(ctx.author, discord.user.User) and
                                               next(filter(lambda role: role.id == ctx.bot.admin_role_id(), ctx.author.roles), None) is not None))
    return commands.check(predicate)
