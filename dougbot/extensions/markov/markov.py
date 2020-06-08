import re
from collections import defaultdict

import requests
from discord import Embed
from discord.ext import commands
import array
import sys
import os
import random
import json
from json.decoder import JSONDecodeError
import string
import copy
from collections import defaultdict

class Markov(commands.Cog):

    _TOTAL = 0  #Occurances of words after the root word
    _WORDS = 1  #Occurances of current word after root word
    _BANNED = ["d!", "dh!", ">>"]
    #wordsDict = defaultdict(lambda:[0, defaultdict(int)])   #{'the': (7, {'wood': 5})}

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def load_json(path):
        try:
            try:
                with open(path,'r') as f:
                    return json.load(f)
            except IOError:
                open(path,'w+')
                return defaultdict(lambda:[0, defaultdict(int)])
        except JSONDecodeError:
            return defaultdict(lambda:[0, defaultdict(int)])

    @staticmethod
    def save_json(markovDict, path):
        with open(path, 'w+') as f:
            json.dump(markovDict, f)
            
    #Adds a new word to the dictionary
    ##markovDict     - Dictionary to populate
    ##rootWord - The initial word
    ##leafWord - The word that comes after the rootWord
    @staticmethod
    def addWordToDict(markovDict, rootWord, leafWord):

        markovDict[rootWord][Markov._WORDS][leafWord] += 1
        markovDict[rootWord][Markov._TOTAL] += 1    
        
    @staticmethod
    def addSentenceToDict(markovDict, sentence):
        prevWord = ""
        #Following line removes punctuation but it might be better to not remove it
        #sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        
        for word in sentence.split():
            word = word.lower()
            Markov.addWordToDict(markovDict, prevWord, word)
            prevWord = word
            
        Markov.addWordToDict(markovDict, prevWord, "")
        
        
    #Populates the dictionary from a file of strings
    ##markovDict     - Dictionary to populate
    ##fileName - string The path to file containing strings
    @staticmethod
    def readFile(markovDict, fileName):
        file = open(fileName, "r", encoding='utf-8')
        
        lines = file.readlines()
        for line in lines:
            Markov.addSentenceToDict(markovDict, line)
        file.close()
        return
           
    #Generates a phrase(chain) from the dictionary
    ##markovDict     - Dictionary containing the words and counts
    ##weighted - Bool Whether a weighted probability based on occurance should be used
    @staticmethod
    def generateChain(markovDict, weighted):
        phrase = ""
        curWord = ""
        length = 0
        
        if weighted: #Control
            curWord = random.choices(list(markovDict[curWord][Markov._WORDS].keys()), weights=list(markovDict[curWord][Markov._WORDS].values()))[0]
            while curWord != "":
                phrase += curWord + " "
                length += 1
                curWord = random.choices(list(markovDict[curWord][Markov._WORDS].keys()), weights=list(markovDict[curWord][Markov._WORDS].values()))[0]
        
        else: #Chaos
            curWord = random.choice(list(markovDict[curWord][Markov._WORDS]))
            while curWord != "":
                phrase += curWord + " "
                length += 1
                curWord = random.choice(list(markovDict[curWord][Markov._WORDS]))
                
        return phrase
        
    #Prints out the dictionary sorted alphabettically along with the count of each word in detail
    ##markovDict     - Dictionary containing the words and counts
    @staticmethod
    def printDict(markovDict):
        for rootWord in sorted(markovDict):
            if rootWord == "":
                print("~STARTING~" + " - " + str(markovDict[rootWord][_TOTAL]))
            else:
                print(rootWord + " - " + str(markovDict[rootWord][_TOTAL]))
                
            for leafWord in sorted(markovDict[rootWord][_WORDS]):
                if leafWord == "":
                    print("~ENDING~" + " - " + str(markovDict[rootWord][_WORDS][leafWord]))
                else:
                    print("\t" + leafWord + " - " + str(markovDict[rootWord][_WORDS][leafWord]))
                
            print("\n")
        return

    @commands.command(aliases=['collect'])
    async def updateFromChat(self, ctx):
        collected = 0
        text_channel = ctx.channel #chat channel
        user = ctx.message.mentions[0]
        
        markovDict = self.load_json(str(user))
        async for message in text_channel.history(limit=None, after=None):
            if message.author == user and not any(x in message.content for x in self._BANNED):
                self.addSentenceToDict(markovDict, message.content)
                collected += 1
        self.save_json(markovDict, str(user))
        await ctx.send("Collected " + str(collected) + " messages from <@" + str(user.id)+ ">")

    @commands.command(aliases=['markov'])
    async def sendToChat(self, ctx):
        collected = 0
        text_channel = ctx.channel #chat channel
        user = ctx.message.mentions[0]
        
        markovDict = self.load_json(str(user))
        
        await ctx.send(self.generateChain(markovDict, True))
        
    @commands.command()
    async def cleanMarkov(self, ctx):
        user = ctx.message.mentions[0]
        markovDict.clear()
        markovDict = self.save_json(str(user))
        
        await ctx.send("Cleared Markov data for <@" + str(user.id) + ">")
        
    @staticmethod
    def testBasics(markovDict):
        #test file reading
        readFile(markovDict, "testFile2.txt")
        printDict(markovDict)
        
        #Test Json I/O
        save_json(markovDict)
        markovDict.clear()
        markovDict = load_json("TestMarkovChainData.txt")
        printDict(markovDict)
        
        #Test chain generation weighted vs unweighted
        print("Control\n---------------")
        for i in range(10):
            print(generateChain(markovDict, True))
        print("\n\nChaos\n---------------")
        for i in range(10):
            print(generateChain(markovDict, False))
        
        
def setup(bot):
    bot.add_cog(Markov(bot))
