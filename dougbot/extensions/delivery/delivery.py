import os
import subprocess

from discord.ext import commands

from dougbot.extensions.util.admin_check import admin_command


class Delivery:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @admin_command()
    async def restart(self, ctx):
        if ctx is None:
            return
        self._restart_bot()

    @commands.command(pass_context=True)
    @admin_command()
    async def update(self, ctx):
        if ctx is None:
            return
        self._update(ctx, ['git', 'pull'])

    @commands.command(pass_context=True)
    @admin_command()
    async def force_update(self, ctx):
        if ctx is None:
            return
        self._update(ctx, ['git', 'fetch', '--all'], ['git', 'reset', '--hard', 'origin/master'])

    def _update(self, ctx, *cmds):
        if ctx is None or cmds is None:
            return
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            self._process_commands(cmds)
            self._restart_bot()
        except subprocess.CalledProcessError:
            if ctx is not None:
                self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)

    @staticmethod
    def _restart_bot():
        p = subprocess.Popen(['reset.bat', str(os.getpid())], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    @staticmethod
    def _process_commands(cmds):
        if cmds is None:
            return
        for command in cmds:
            subprocess.check_call(command)


def setup(bot):
    bot.add_cog(Delivery(bot))
