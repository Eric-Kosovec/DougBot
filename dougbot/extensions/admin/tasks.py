from nextcord.ext import commands

from dougbot.core.bot import DougBot


class Tasks(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot

    @commands.group()
    async def task(self, ctx):
        pass

    @task.command()
    async def list(self):
        pass

    @task.command()
    async def modify(self):
        pass

    @task.command()
    async def stop(self):
        pass


def setup(bot: DougBot):
    bot.add_cog(Tasks(bot))
