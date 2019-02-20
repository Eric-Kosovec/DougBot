import os
import subprocess

from discord.ext import commands


class ContinuousDeliverySystem:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def update(self, ctx):
        if ctx is None:
            return

        cwd = os.getcwd()
        os.chdir('../..')
        try:
            subprocess.check_call(['git', 'checkout', '-f', 'master'])
        except subprocess.CalledProcessError:
            await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)

        # Pull from github
        # Restart ourself

    @staticmethod
    async def _are_updates():
        pass


def setup(bot):
    bot.add_cog(ContinuousDeliverySystem(bot))
