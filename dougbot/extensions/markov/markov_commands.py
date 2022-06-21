import os
from datetime import datetime

from nextcord import Embed
from nextcord import TextChannel
from nextcord import User
from nextcord.ext import commands

from dougbot.config import EXTENSION_RESOURCES_DIR
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotation.admincheck import admin_command
from dougbot.extensions.markov.markov_lib import *


class Markov(commands.Cog):
    # Static variables
    _TIMESTAMPEXT = ".timestamp"
    _CHAINSEXT = ".chains"
    _BANNED = ["d!", "d#", "d$", "dh!", ">>", "!s", ".horo", "!trump", "!autojoin", "!autoleave", "!join", "!leave", "!echo", "!autosave", "(>"]

    # <:NAME:ID>
    # Custom emoji structure
    _THINKING_EMOJI = '\U0001F914'
    _INTERROBANG = '\U00002049'
    _CHECKMARK = '\U00002714'

    def __init__(self, bot: DougBot):
        self.bot = bot
        self._chains_dir = os.path.join(EXTENSION_RESOURCES_DIR, 'markov', 'chains')

    @commands.command()
    async def markov(self, ctx, userOne: User, userTwo: User = None):
        length = 0
        attempts = 0
        existingDict = False
        phrase = ""
        text_channel = ctx.channel  # chat channel

        markovDict, existingDict = await MarkovLib.load_pickle(os.path.join(self._chains_dir, str(userOne) + Markov._CHAINSEXT))
        if existingDict:
            while (phrase == '' or length < 5) and attempts < 10:  # Generate new phrase if last one sucked
                try:
                    phrase, length = await MarkovLib.generateChain(markovDict, True)
                except KeyError:  # On error just make a new phrase (I'll fix this later maybe)
                    continue

            if attempts >= 10:
                await ctx.send("Exceeded number of attempts for " + str(userOne))
            else:
                embed = Embed(title=':speaking_head: Markov :person_shrugging:', color=0x228B22)
                embed.add_field(name=str(userOne), value=phrase.capitalize())
                await ctx.send(embed=embed)
        else:
            await ctx.send("No existing Markov dictionary for " + str(userOne) + ".\nUse \"d!collect <@" + str(userOne.id) + ">\"")

    @commands.command()
    async def collect(self, ctx, user: User, text_channel: TextChannel = None):
        message = None
        timeStamps = {}
        lastTimestamp = None
        collected = 0
        existingDict = False
        dictExistanceString = ""

        if text_channel is None:  # If no text channel specified then use the one called from
            text_channel = ctx.channel  # chat channel

        collectMsg = await ctx.send("Collecting messages from <@" + str(user.id) + ">")
        thinkingReact = await collectMsg.add_reaction(Markov._THINKING_EMOJI)

        try:
            markovDict, existingDict = await MarkovLib.load_pickle(os.path.join(self._chains_dir, str(user) + Markov._CHAINSEXT))

            # If Dictionary exists then load the timestamp dictionary
            if existingDict:
                timeStamps, _ = await MarkovLib.load_json(os.path.join(self._chains_dir, str(user) + Markov._TIMESTAMPEXT))
                lastTimestamp = timeStamps.get(text_channel.name)
                if lastTimestamp:
                    lastTimestamp = datetime.strptime(timeStamps[text_channel.name], '%Y-%m-%d %H:%M:%S.%f')

            async for message in text_channel.history(limit=None, after=lastTimestamp, oldest_first=True):
                if (message.author == user  # From the user specified
                        and not any(symbol in message.content for symbol in Markov._BANNED)  # Does not contain symbols from banned list
                        and len(message.content.split()) > 1  # Is long enough to produce a chain
                ):
                    await MarkovLib.addSentenceToDict(markovDict, message.clean_content)
                    collected += 1

            if message is not None:  # Throws error on case where no messages are read in
                timeStamps[text_channel.name] = str(message.created_at)
                await MarkovLib.save_json(timeStamps, os.path.join(self._chains_dir, str(user) + Markov._TIMESTAMPEXT))
            if collected != 0:  # Dont Bother updating if no new messages
                await MarkovLib.save_pickle(markovDict, os.path.join(self._chains_dir, str(user) + Markov._CHAINSEXT))

            # Output
            if existingDict:
                dictExistanceString = "**Updated:** "
            else:
                dictExistanceString = "**New:** "
            await ctx.send(dictExistanceString + "Collected " + str(collected) + " message(s) from <@" + str(user.id) + "> from " + str(text_channel.name) + ".")
            await collectMsg.delete()
        except ValueError as e:
            await collectMsg.remove_reaction(Markov._THINKING_EMOJI, collectMsg.author)
            await collectMsg.add_reaction(Markov._INTERROBANG)
            raise e

    @commands.command(help='Lists all the chains currently gathered')
    async def chains(self, ctx):
        files = []
        onlyNames = []
        for (_, _, filenames) in os.walk(self._chains_dir):
            files.extend(filenames)
            break
        for file in files:
            if Markov._CHAINSEXT in file:
                onlyNames.append(os.path.splitext(file)[0])
        await ctx.send('\n'.join(onlyNames))

    # Deletes the chain file for given user
    @commands.command()
    @admin_command()
    async def clean_chain(self, ctx, user: User):
        try:
            os.remove(os.path.join(self._chains_dir, str(user) + Markov._CHAINSEXT))
            os.remove(os.path.join(self._chains_dir, str(user) + Markov._TIMESTAMPEXT))

            await ctx.send("Cleared Markov data for <@" + str(user.id) + ">")
        except FileNotFoundError:
            await ctx.send("No chains exist for " + str(user) + ".")


def setup(bot):
    bot.add_cog(Markov(bot))
    
