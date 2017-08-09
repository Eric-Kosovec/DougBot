import discord
from discord.channel import *
from discord.ext import commands

from DougBotProperties import *

client = commands.Bot(description=DESCRIPTION, command_prefix=COMMAND_PREFIX)


class DougBot(discord.Client):
    def __init__(self):
        super().__init__()

        return


@client.event
async def on_ready():
    # init_logger()

    print("Bot online")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    print("-----------------------")


@client.command(pass_context=True)
async def ping(ctx):
    await client.say("pong")


@client.command(pass_context=True)
async def join(ctx):
    channel = discord.utils.get(client.get_all_channels(), name='SadDoug Central', type=ChannelType.voice)
    client.join_voice_channel(channel)


@client.command(pass_context=True)
async def leave(ctx):
    channel = discord.utils.get(client.get_all_channels(), name='SadDoug Central', type=ChannelType.voice)
    voice_client = client.voice_client_in(channel.server)
    if voice_client is not None:
        await voice_client.disconnect()
    return


@client.command(pass_context=True)
async def slap(ctx, args):
    await client.say("You slapped {}".format(args))


@client.command(pass_context=True)
async def github(ctx):
    await client.say(GITHUB)


client.run(TOKEN)
