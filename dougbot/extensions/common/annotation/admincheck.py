import discord
from discord import Member
from discord.ext import commands

from dougbot import config


def admin_command():
    async def has_admin_role(ctx):
        admin_role_id = config.get_configuration().admin_role_id
        return ctx.me.id == ctx.author.id or _has_role(ctx, admin_role_id)

    return commands.check(has_admin_role)


def mod_command():
    async def has_mod_role(ctx):
        return ctx.me.id == ctx.author.id or \
               _has_role(ctx, config.get_configuration().admin_role_id, config.get_configuration().mod_role_id)

    return commands.check(has_mod_role)


def _has_role(ctx, *role_ids):
    return isinstance(ctx.author, Member) and discord.utils.find(lambda r: r.id in role_ids, ctx.author.roles)
