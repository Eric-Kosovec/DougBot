import os
import subprocess

from discord.ext import commands

from dougbot.extensions.util.admin_check import admin_command


class Delivery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=False)
    @admin_command()
    async def restart(self, ctx):
        _ = ctx
        await self._restart_bot()

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
    async def update_dependencies(self, ctx):
        await self._update(ctx, ['python', os.path.join(self.bot.ROOT_DIR, 'update_deps.py')])

    async def _update(self, ctx, *cmds):
        if ctx is None or cmds is None:
            return
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            await self._process_commands(cmds)
            await self._restart_bot()
        except subprocess.CalledProcessError:
            if ctx is not None:
                self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)

    async def _restart_bot(self):
        p = subprocess.Popen(['reset.bat', str(os.getpid())], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    @staticmethod
    async def _process_commands(cmds):
        if cmds is None:
            return
        for command in cmds:
            subprocess.check_call(command)


def setup(bot):
    bot.add_cog(Delivery(bot))
