from DougBotProperties import *
from discord.ext import commands

client = commands.Bot(description=DESCRIPTION, command_prefix=COMMAND_PREFIX)


@client.event
async def on_ready():
    print("Bot online")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))


@client.command(pass_context=True)
async def ping(ctx):
    await client.say("/tts vwvwvwvw")


@client.command(pass_context=True)
async def slap(ctx, args):
    await client.say("You slapped {}".format(args))


@client.command(pass_context=True)
async def github(ctx):
    await client.say(GITHUB)


client.run(TOKEN)
