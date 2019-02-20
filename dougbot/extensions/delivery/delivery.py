import os
import subprocess

from discord.ext import commands


class ContinuousDeliverySystem:

    def __init__(self, bot, days_per_week=7):
        self.days_per_week = days_per_week
        self.bot = bot

    @commands.command(pass_context=True)
    async def schedule_updates(self, ctx, days_per_week: int=7):
        if ctx is None:
            return
        pass

    @commands.command(pass_context=True)
    async def update(self, ctx):
        if ctx is None:
            return

        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'pull'])

            # Restart ourself
            pid = os.getpid()
            print(pid)

            p = subprocess.Popen(['reset.bat', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except subprocess.CalledProcessError:
            await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)


def setup(bot):
    bot.add_cog(ContinuousDeliverySystem(bot))
