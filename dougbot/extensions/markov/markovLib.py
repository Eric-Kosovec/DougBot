import re
import string
import copy
import requests
import array
import sys
import os
import random
import json

from discord import Embed
from discord.ext import commands

from collections import defaultdict
from json.decoder import JSONDecodeError

#Generates Markov chains from discord chat
##Dictionary Template: defaultdict(lambda:[0, defaultdict(int)])   #{'the': (7, {'wood': 5})}
class markov():

#Static variables
    _TOTAL  = 0  #Occurances of words after the root word
    _WORDS  = 1  #Occurances of current word after root word

    @staticmethod
    def load_json(path):
        try:
            try:
                with open(path,'r') as f:
                    markovDict = json.load(f)
                    f.close()
                    return markovDict, True
            except IOError:
                open(path,'w+').close()
                return defaultdict(lambda:[0, defaultdict(int)]), False
        except JSONDecodeError:
            return defaultdict(lambda:[0, defaultdict(int)]), False

    @staticmethod
    def save_json(markovDict, path):
        with open(path, 'w+') as f:
            json.dump(markovDict, f)
            f.close()
            
    #Adds a new word to the dictionary
    ##markovDict    - Dictionary to populate
    ##rootWord      - The initial word
    ##leafWord      - The word that comes after the rootWord
    @staticmethod
    def addWordToDict(markovDict, rootWord, leafWord):

        markovDict[rootWord][Markov._WORDS][leafWord] += 1
        markovDict[rootWord][Markov._TOTAL] += 1    

    @staticmethod
    def addSentenceToDict(markovDict, sentence):
        prevWord = ""
        #Following line removes punctuation but it might be better to not remove it
        #sentence = sentence.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
        
        sentenceList = re.findall(r"[\w']+|[.,!?;]", sentence)
        
        for word in sentenceList:
            word = word.lower()
            markov.addWordToDict(markovDict, prevWord, word)
            prevWord = word
            
        if(prevWord not in string.punctuation):
            markov.addWordToDict(markovDict, prevWord, ".")

    #Populates the dictionary from a file of strings
    ##markovDict     - Dictionary to populate
    ##fileName - string The path to file containing strings
    @staticmethod
    def readFile(markovDict, fileName):
        file = open(fileName, "r", encoding='utf-8')
        
        lines = file.readlines()
        for line in lines:
            markov.addSentenceToDict(markovDict, line)
        file.close()
        return

    #Generates a phrase(chain) from the dictionary
    ##markovDict    - Dictionary containing the words and counts
    ##weighted      - Bool Whether a weighted probability based on occurance should be used
    @staticmethod
    def generateChain(markovDict, weighted):
        phrase = ""
        curWord = ""
        length = 0
        
        if weighted: #Control
            while curWord not in [".", "!", "?"]:
                curWord = random.choices(list(markovDict[curWord][markov._WORDS].keys()), weights=list(markovDict[curWord][markov._WORDS].values()))[0]
                if(curWord not in string.punctuation and length > 0):
                    phrase += " "
                phrase += curWord
                length += 1
                
        else: #Chaos
            while curWord not in [".", "!", "?"]:
                curWord = random.choice(list(markovDict[curWord][markov._WORDS]))
                if(curWord not in string.punctuation and length > 0):
                    phrase += " "
                phrase += curWord
                length += 1
                
        return phrase, length

    #Prints out the dictionary sorted alphabettically along with the count of each word in detail
    ##markovDict     - Dictionary containing the words and counts
    @staticmethod
    def printDict(markovDict):
        for rootWord in sorted(markovDict):
            if rootWord == "":
                print("~STARTING~" + " - " + str(markovDict[rootWord][markov._TOTAL]))
            else:
                print(rootWord + " - " + str(markovDict[rootWord][markov._TOTAL]))
                
            for leafWord in sorted(markovDict[rootWord][markov._WORDS]):
                if leafWord == "":
                    print("~ENDING~" + " - " + str(markovDict[rootWord][markov._WORDS][leafWord]))
                else:
                    print("\t" + leafWord + " - " + str(markovDict[rootWord][markov._WORDS][leafWord]))
                
            print("\n")
        return

    @staticmethod
    def testBasics(markovDict):
        #test file reading
        markov.readFile(markovDict, "testFile2.txt")
        markov.printDict(markovDict)
        
        #Test Json I/O
        markov.save_json(markovDict)
        markovDict.clear()
        markovDict = Markov.load_json("TestMarkovChainData.txt")
        markov.printDict(markovDict)
        
        #Test chain generation weighted vs unweighted
        print("Control\n---------------")
        for i in range(10):
            print(markov.generateChain(markovDict, True))
        print("\n\nChaos\n---------------")
        for i in range(10):
            print(markov.generateChain(markovDict, False))

