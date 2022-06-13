import asyncio

from nextcord.ext import commands
from nextcord.ext.commands import Context

from dougbot.common.messaging import reactions
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotation.admincheck import admin_command


class ExtensionAdmin(commands.Cog):
    _READONLY_EXTENSIONS = {'Debug', 'ExtensionAdmin', 'Resources', 'Update'}

    def __init__(self, bot: DougBot):
        self.bot = bot
        self._disabled_cogs = {}

    @commands.group(aliases=['extensions'], case_insensitive=True)
    @admin_command()
    async def extension(self, _):
        pass

    @extension.command()
    @admin_command()
    async def list(self, ctx: Context):
        enabled_cogs = [c for c in self.bot.cogs.keys()]
        enabled_cogs.sort()

        disabled_cogs = [c for c in self._disabled_cogs.keys()]
        disabled_cogs.sort()

        cog_list = '**Enabled Extensions:**\n' + '\n'.join(enabled_cogs)

        if len(disabled_cogs):
            cog_list += '\n\n**Disabled Extensions:**\n' + '\n'.join(disabled_cogs)

        await ctx.send(cog_list)

    @extension.command()
    @admin_command()
    async def status(self, ctx: Context, name: str):
        is_disabled = name in self._disabled_cogs
        await ctx.send(f"{name} is {'disabled' if is_disabled else 'enabled'}")

    @extension.command()
    @admin_command()
    async def enable(self, ctx, name: str):
        await self.enable_for(ctx, name)

    @extension.command()
    @admin_command()
    async def enable_for(self, ctx: Context, name: str, seconds: int = 0, minutes: int = 0, hours: int = 0):
        if name in self._READONLY_EXTENSIONS:
            return

        if name in self._disabled_cogs:
            self.bot.add_cog(self._disabled_cogs[name])
            del self._disabled_cogs[name]

            if seconds or minutes or hours:
                await asyncio.sleep(seconds + minutes * 60 + hours * 3600)
                await self.disable(ctx, name)

    @extension.command()
    @admin_command()
    async def disable(self, ctx, name: str):
        await self.disable_for(ctx, name)

    @extension.command()
    @admin_command()
    async def disable_for(self, ctx: Context, name: str, seconds: int = 0, minutes: int = 0, hours: int = 0):
        if name in self._READONLY_EXTENSIONS:
            await reactions.confusion(ctx.message, f'{name} is read-only', delete_text_after=5)
            return

        cog = self.bot.remove_cog(name)
        if cog:
            self._disabled_cogs[name] = cog
            await reactions.confirmation(ctx.message)

            if seconds or minutes or hours:
                await asyncio.sleep(seconds + minutes * 60 + hours * 3600)
                await self.enable(ctx, name)

    @extension.command()
    @admin_command()
    async def restart(self, ctx: Context, name: str):
        if name in self._disabled_cogs:
            await reactions.confusion(ctx.message, f'{name} is disabled', delete_text_after=5)
            return

        await self.disable(ctx, name)
        await self.enable(ctx, name)
        await reactions.confirmation(ctx.message)


def setup(bot: DougBot):
    bot.add_cog(ExtensionAdmin(bot))
