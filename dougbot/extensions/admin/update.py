import os
import subprocess
import sys

from discord.ext import commands

from dougbot.common import reactions
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotations.admincheck import admin_command


class Update(commands.Cog):

    def __init__(self, bot: DougBot):
        self._bot = bot

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
                await self._update(ctx, [python_name, os.path.join(self._bot.ROOT_DIR, 'setup.py')])
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
        os.chdir(self._bot.ROOT_DIR)
        try:
            await self._process_commands(['git', 'fetch', '--all'])
            await self._process_commands(*cmds)
            await self._restart_bot(ctx)
        finally:
            os.chdir(cwd)

    @staticmethod
    async def _restart_bot(ctx):
        await ctx.message.delete()
        os.execl(sys.executable, sys.executable, *sys.argv)
        await ctx.send('Failed to restart')

    @staticmethod
    async def _process_commands(*cmds):
        for command in cmds:
            subprocess.call(command)


def setup(bot):
    bot.add_cog(Update(bot))
