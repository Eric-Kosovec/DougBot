import discord
from discord.channel import *
from discord.ext import commands

from DougBotProperties import *

client = commands.Bot(description=DESCRIPTION, command_prefix=COMMAND_PREFIX)

user_dict = dict()

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


@client.command(pass_context=True)
async def putdict(ctx, args):
    strs = args.split(":")
    key = strs[0]
    value = strs[1]
    user_dict[key] = value
    await client.say("{} : {} inserted into dictionary.".format(key, value))


@client.command(pass_context=True)
async def querydict(ctx, args):
    if args in user_dict:
        await client.say("{} found in dictionary.".format(args))
    else:
        await client.say("{} not found in dictionary.".format(args))


@client.command(pass_context=True)
async def removedict(ctx, args):
    try:
        value = user_dict[args]
        del user_dict[args]
        await client.say("{} : {} not removed from dictionary.".format(args, value))
    except KeyError:
        await client.say("{} not found in dictionary.".format(args))


@client.command(pass_context=True)
async def cleardict(ctx):
    user_dict.clear()
    await client.say("Dictionary cleared.")


@client.command(pass_context=True)
async def dictsize(ctx):
    await client.say("{}".format(len(user_dict)))


@client.command(pass_context=True)
async def printdict(ctx):
    dict_str = "["

    for (key, value) in user_dict.items():
        dict_str += " " + key + ":" + value

    dict_str += " ]"

    await client.say(dict_str)

client.run(TOKEN)
