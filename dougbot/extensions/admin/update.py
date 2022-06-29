import os
import shutil
import subprocess
import sys

from nextcord import Status
from nextcord.ext import commands

from dougbot.common.messaging import reactions
from dougbot.config import ROOT_DIR
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotation.admincheck import admin_command


class Update(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def restart(self, ctx):
        await self._restart_bot(ctx)

    @commands.command()
    @admin_command()
    async def update(self, ctx):
        await self._update(ctx, ['git', 'fetch', '--all'], ['git', 'pull'])

    @commands.command()
    @admin_command()
    async def update_force(self, ctx):
        await self._update(ctx, ['git', 'fetch', '--all'], ['git', 'reset', '--hard', 'origin/master'])

    @commands.command()
    @admin_command()
    async def update_libs(self, ctx):
        python_names = ['python', 'python3']
        first_exception = None
        error_count = 0

        for python_name in python_names:
            try:
                await self._update(ctx, [python_name, os.path.join(ROOT_DIR, 'setup.py')])
                break
            except Exception as e:
                if first_exception is None:
                    first_exception = e
                error_count += 1

        if error_count >= len(python_names):
            await reactions.confusion(ctx.message)
            raise first_exception

        await self._restart_bot(ctx)

    async def _update(self, ctx, *cmds):
        cwd = os.getcwd()
        os.chdir(ROOT_DIR)
        try:
            await self._process_commands(*cmds)
            await self._restart_bot(ctx)
        finally:
            os.chdir(cwd)

    async def _restart_bot(self, ctx):
        await ctx.message.delete(delay=3)
        await self.bot.change_presence(status=Status.offline)
        os.execl(sys.executable, sys.executable, *sys.argv)
        await ctx.send('Failed to restart')

    @staticmethod
    async def _process_commands(*cmds):
        for command in cmds:
            subprocess.call(command)

    async def _spawn_secondary(self):
        python_path = await self._which_python()
        if python_path is None:
            return

        subprocess.Popen([python_path, os.path.join(ROOT_DIR, 'run.py')])

    @staticmethod
    async def _which_python():
        pythons = ['python3', 'python', 'py']
        for python in pythons:
            python_path = shutil.which(python)
            if python_path is not None and 'WindowsApps' not in python_path:
                return python_path

        return None


def setup(bot):
    bot.add_cog(Update(bot))
