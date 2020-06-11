import re
import string
import copy
import requests
import array
import sys
import os
import random
import json
from datetime import datetime

from dougbot.extensions.markov.markovLib import *

from discord import Embed
from discord.ext import commands

from json.decoder import JSONDecodeError

#Module attached to markov.py to allow interactions through discord
class markovCommands(commands.Cog):

#Static variables
    _TIMESTAMPEXT   = ".timestamp"
    _CHAINSEXT      = ".chains"
    _BANNED         = ["d!", "dh!", ">>", "!s", ".horo", "!trump", "d#", "!autojoin", "!autoleave", "!join", "!leave", "!echo", "!autosave", "(>"]
    
    _THINKING_EMOJI = '\U0001F914'
    _INTERROBANG    = '\U00002049'
    _CHECKMARK      = '\U00002714'

    def __init__(self, bot):
        self.bot = bot
        self._chains_dir = os.path.join(self.bot.ROOT_DIR, 'resources', 'chains')
        
    @commands.command(aliases=['collect'])
    async def updateFromChat(self, ctx):
        message = None
        lastTimestamp = None
        collected = 0
        existingDict = False
        dictExistanceString = ""
        
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
            text_channel = ctx.channel #chat channel
            collectMsg = await ctx.send("Collecting messages from <@" + str(user.id)+ ">")
            thinkingReact = await collectMsg.add_reaction(markovCommands._THINKING_EMOJI)
            
            try:
                markovDict, existingDict = markov.load_json(os.path.join(self._chains_dir, str(user) + markovCommands._CHAINSEXT))
                    
                if existingDict:
                    lastTimestamp = datetime.strptime(markov.load_json(os.path.join(self._chains_dir, str(user) + markovCommands._TIMESTAMPEXT))[0], '%Y-%m-%d %H:%M:%S.%f')
                    
                async for message in text_channel.history(limit=None, after=lastTimestamp, oldest_first=True):
                    if (message.author == user                              #From the user specified
                    and not any(symbol in message.content for symbol in markovCommands._BANNED) #Does not contain symbols from banned list
                    and len(message.content.split()) > 1                    #Is long enough to produce a chain
                    ):
                        markov.addSentenceToDict(markovDict, message.clean_content)
                        collected += 1
                        
                markov.save_json(str(message.created_at), os.path.join(self._chains_dir, str(user) + markovCommands._TIMESTAMPEXT))
                markov.save_json(markovDict, os.path.join(self._chains_dir, str(user) + markovCommands._CHAINSEXT))
                
                if existingDict:
                    dictExistanceString = "**Updated:** "
                else:
                    dictExistanceString = "**New:** "
                await ctx.send(dictExistanceString + "Collected " + str(collected) + " message(s) from <@" + str(user.id)+ ">")
                await collectMsg.delete()
            except ValueError as e:
                await collectMsg.remove_reaction(markovCommands._THINKING_EMOJI, collectMsg.author)
                await collectMsg.add_reaction(markovCommands._INTERROBANG)
                raise e
        else:
            await ctx.send("No user parameter given.\nUse \"d!collect @User\"")
            
    @commands.command(aliases=['markov', 'impersonate'])
    async def sendToChat(self, ctx):
        if ctx.message.mentions:
            length = 0
            attempts = 0
            existingDict = False
            phrase = ""
            text_channel = ctx.channel #chat channel
            user = ctx.message.mentions[0]
            
            markovDict, existingDict = markov.load_json(os.path.join(self._chains_dir, str(user) + markovCommands._CHAINSEXT))
            if existingDict:
                while((phrase == "" or length < 5) and attempts < 10): #Generate new phrase if last one sucked
                    phrase, length = markov.generateChain(markovDict, True)
                    
                if attempts >= 10:
                    await ctx.send("Exceeded number of attempts for " + str(user))
                else:
                    embed = Embed(title="", color=0x228B22)
                    embed.add_field(name=str(user), value=phrase.capitalize())
                    await ctx.send(embed=embed)
            else:
                await ctx.send("No existing Markov dictionary for " + str(user) + ".\nUse \"d!collect <@" + str(user.id)+ ">\"")
        else:
            await ctx.send("No user parameter given.\nUse \"d!markov @User\"")
        
    @commands.command(aliases=['clean'])
    async def cleanMarkov(self, ctx):
        try:
            if ctx.message.mentions:
                user = ctx.message.mentions[0]
                os.remove(os.path.join(self._chains_dir, str(user) + markovCommands._CHAINSEXT))
                os.remove(os.path.join(self._chains_dir, str(user) + markovCommands._TIMESTAMPEXT))
                
                await ctx.send("Cleared Markov data for <@" + str(user.id) + ">")
            else:
                await ctx.send("No user parameter given.\nUse \"d!clean @User\"")
        except FileNotFoundError:
            await ctx.send("No chains exist for " + str(user) + ".")

def setup(bot):
    bot.add_cog(markovCommands(bot))
