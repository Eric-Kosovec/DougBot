from DougBotProperties import *
from discord.ext import commands

client = commands.Bot(description=DESCRIPTION, command_prefix=COMMAND_PREFIX)


@client.event
async def on_ready():
    print("Works")


@client.command(pass_context=True)
async def ping(ctx):
    await client.say("pong")


@client.command(pass_context=True)
async def slap(ctx, args):
    await client.say("You slapped {}".format(args))


@client.command(pass_context=True)
async def github(ctx):
    await client.say("https://github.com/Eric-Kosovec/DougBot")


client.run(TOKEN)
