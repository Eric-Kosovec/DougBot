import os
import subprocess
import sys

from discord.ext import commands

from dougbot.extensions.common.annotations.admincheck import admin_command


class Delivery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def restart(self, ctx):
        await self._restart_bot(ctx)

    @commands.command()
    @admin_command()
    async def update(self, ctx):
        await self._update(ctx, ['git', 'pull'])

    @commands.command()
    @admin_command()
    async def force_update(self, ctx):
        await self._update(ctx, ['git', 'reset', '--hard', 'origin/master'])

    @commands.command()
    @admin_command()
    async def update_pkgs(self, ctx):
        await self._update(ctx, ['python3', os.path.join(self.bot.ROOT_DIR, 'setup.py')])
        await self._restart_bot(ctx)

    async def _update(self, ctx, *cmds):
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)

        try:
            await self._process_commands(['git', 'fetch', '--all'])
            await self._process_commands(*cmds)
            await self._restart_bot(ctx)
        except Exception as e:
            await self.bot.confusion(ctx.message)
            raise e
        finally:
            os.chdir(cwd)

    @staticmethod
    async def _restart_bot(ctx):
        await ctx.send('Restarting...')
        os.execl(sys.executable, sys.executable, *sys.argv)
        await ctx.send('Failed to restart')

    @staticmethod
    async def _process_commands(*cmds):
        for command in cmds:
            subprocess.call(command)


def setup(bot):
    bot.add_cog(Delivery(bot))
