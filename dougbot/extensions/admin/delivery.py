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
        await self._update(ctx, ['git', 'fetch', '--all'], ['git', 'reset', '--hard', 'origin/master'])

    @commands.command()
    @admin_command()
    async def update_pkgs(self, ctx):
        await self._update(ctx, ['python', os.path.join(self.bot.ROOT_DIR, 'setup.py')])
        await self._restart_bot(ctx)

    async def _update(self, ctx, *cmds):
        if ctx is None or cmds is None:
            return

        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)

        # Find which files will change - core files or extensions.
        # Extensions can be reloaded, core files require restarting
        await self._process_commands(['git', 'fetch'])
        subprocess.check_output(['git', 'diff', 'master', 'origin/master', '--name-only'])

        # Update code
        try:
            await self._process_commands(*cmds)
        except subprocess.CalledProcessError:
            if ctx is not None:
                await self.bot.confusion(ctx.message)
                os.chdir(cwd)
                return

        await self._restart_bot(ctx)
        os.chdir(cwd)  # Just in case restarting fails

    @staticmethod
    async def _restart_bot(ctx):
        await ctx.send('Restarting...')
        os.execl(sys.executable, sys.executable, *sys.argv)
        await ctx.send('Failed to restart')

    @staticmethod
    async def _process_commands(*cmds):
        if cmds is None:
            return
        for command in cmds:
            subprocess.call(command)


def setup(bot):
    bot.add_cog(Delivery(bot))
