
from discord import File
from discord.ext import commands

from dougbot.extensions.util.admin_check import admin_command


class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def readlog(self, ctx):
        try:
            with open(self.bot.LOG_PATH, 'r') as fd:
                logdata = fd.read()
            await ctx.send(f'Log Contents:\n{logdata}')
        except Exception as e:
            await ctx.send(f'Error reading logfile: {e}')

    @commands.command()
    @admin_command()
    async def getlog(self, ctx):
        # Upload in private message
        try:
            dmchannel = await ctx.author.create_dm()
            await dmchannel.send(file=File(self.bot.LOG_PATH))
        except Exception as e:
            await ctx.send(f'Error sending logfile: {e}')

    @commands.command()
    @admin_command()
    async def clearlog(self, ctx):
        try:
            # Wipe log contents
            open(self.bot.LOG_PATH, 'w').close()
        except Exception as e:
            await ctx.send(f'Error clearing logfile: {e}')


def setup(bot):
    bot.add_cog(Debug(bot))
