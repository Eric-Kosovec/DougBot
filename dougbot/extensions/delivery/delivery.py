import os
import subprocess
import sys

from discord.ext import commands


class Delivery:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def push(self, ctx):
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'add', 'dougbot/res'])
            subprocess.check_call(['git', 'commit', '-m', 'Pushed resources by bot.'])
            subprocess.check_call(['git', 'push'])
        except subprocess.CalledProcessError or subprocess.SubprocessError:
            if ctx is not None:
                await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)

    @commands.command(pass_context=True)
    async def update(self, ctx):
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'pull'])

            pid = os.getpid()

            # Restart ourself
            p = subprocess.Popen(['reset.bat', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except subprocess.CalledProcessError:
            if ctx is not None:
                await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)

    def _soft_update(self):
        # TODO ISSUE IS WE LOSE THE SCHEDULE IF DONE, SO NEED A KVSTORE
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'pull'])

            pid = os.getpid()

            # Restart ourself
            p = subprocess.Popen(['reset.bat', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except subprocess.CalledProcessError:
            print('Scheduled soft update failed.', file=sys.stderr)
        finally:
            os.chdir(cwd)

    @commands.command(pass_context=True)
    async def force_update(self, ctx):
        if ctx is None:
            return

        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'fetch', '--all'])
            subprocess.check_call(['git', 'reset', '--hard', 'origin/master'])

            pid = os.getpid()

            # Restart ourself
            p = subprocess.Popen(['reset.bat', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except subprocess.CalledProcessError:
            await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)


def setup(bot):
    bot.add_cog(Delivery(bot))
