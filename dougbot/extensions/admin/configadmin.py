
from nextcord.ext import commands
from nextcord.ext.commands import Context

from dougbot import config
from dougbot.common.messaging import reactions
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotation.admincheck import admin_command


class ConfigAdmin(commands.Cog):
    _PRIVATE_CONFIGS = {'token'}
    _NO_DELETE_CONFIGS = {'command_prefix', 'admin_role_id', 'mod_role_id', 'debug_channel_id', 'logging_channel_id'}

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.group(aliases=['configs'], case_insensitive=True)
    @admin_command()
    async def config(self, ctx: Context):
        # TODO SAVE TO CONFIG FILE?
        #  CONFIGS IN DB TOO?
        pass

    @config.command()
    @admin_command()
    async def add(self, ctx: Context, name: str, *, value: str):
        configs = vars(config.get_configuration())
        if name in configs:
            await reactions.confusion(ctx.message, f"'{name}' is already in configs")
            return
        configs[name] = value
        await reactions.confirmation(ctx.message)

    @config.command()
    @admin_command()
    async def list(self, ctx: Context):
        configs = {k: v for k, v in vars(config.get_configuration()).items() if k not in self._PRIVATE_CONFIGS}
        await ctx.send(f'{configs}')  # TODO BETTER OUTPUT AND MAYBE ONLY TO ADMIN CHANNEL

    @config.command()
    @admin_command()
    async def remove(self, ctx: Context, name: str):
        if name in self._PRIVATE_CONFIGS or name in self._NO_DELETE_CONFIGS:
            await reactions.confusion(ctx.message, f"'{name}' can't be deleted")
            return

        configs = vars(config.get_configuration())
        if name in configs:
            del configs[name]
        await reactions.confirmation(ctx.message)

    @config.command()
    @admin_command()
    async def replace(self, ctx: Context, name: str, *, value: str):
        if name in self._PRIVATE_CONFIGS:
            await reactions.confusion(ctx.message, f"'{name}' is a private config")
            return
        vars(config.get_configuration())[name] = value
        await reactions.confirmation(ctx.message)


def setup(bot: DougBot):
    bot.add_cog(ConfigAdmin(bot))
