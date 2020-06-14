import re
import string
import copy
import array
import sys
import os
import random
import json

from json.decoder import JSONDecodeError

#Generates Markov chains from discord chat
##Dictionary Template: defaultdict(lambda:[0, defaultdict(int)])   #{'the': (7, {'wood': 5})}
##Dictionary Template: dict{rootWord:[rootCount, dict{leafWord:leafCount}]}   #{'the': (7, {'wood': 5})}
class Markov():

#Static variables
    _TOTAL  = 0  #Occurances of words after the root word
    _WORDS  = 1  #Occurances of current word after root word
    _ENDPUNCTUATION = ['.', '!', '?', '\n']
    _SYMBOLS = ['.','-',',','!','?','(','_',')', '[', ']', '{', '}', '+', '=', '*', '/', '\\', '#', '$', '%', '^', '&', ';', '\'', '"', '`', '~']
    
    @staticmethod
    def load_json(path):
        try:
            try:
                with open(path,'r') as f:
                    jsonObj = json.load(f)
                    f.close()
                    return jsonObj, True
            except IOError:
                return {}, False
        except JSONDecodeError:
            return {}, False

    @staticmethod
    def save_json(jsonObj, path):
        with open(path, 'w+') as f:
            json.dump(jsonObj, f)
            f.close()
            
    #Adds a new word to the dictionary
    ##markovDict    - Dictionary to populate
    ##rootWord      - The initial word
    ##leafWord      - The word that comes after the rootWord
    @staticmethod
    def addWordToDict(markovDict, rootWord, leafWord):
        if rootWord not in markovDict:
            markovDict[rootWord] = [0, {leafWord: 0}]
        if leafWord not in markovDict[rootWord][Markov._WORDS]:
            markovDict[rootWord][Markov._WORDS][leafWord] = 0
        markovDict[rootWord][Markov._TOTAL] += 1
        markovDict[rootWord][Markov._WORDS][leafWord] += 1

    @staticmethod
    def addSentenceToDict(markovDict, sentence):
        prevWord = ""
        
        #Following line removes punctuation but it might be better to not remove it
        #sentence = sentence.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
        
        #Seperates all symbols and words
        #sentenceList = re.findall(r"[\w']+|[.,!?;]", sentence)
        
        for spaced in Markov._SYMBOLS:
            sentence = sentence.replace(spaced, ' {0} '.format(spaced))
        
        for word in sentence.split():
            word = word.lower()
            Markov.addWordToDict(markovDict, prevWord, word)
            prevWord = word
            if word in Markov._ENDPUNCTUATION:
                prevWord = "."
            
        if(prevWord not in string.punctuation):
            Markov.addWordToDict(markovDict, prevWord, ".")

    #Populates the dictionary from a file of strings
    ##markovDict     - Dictionary to populate
    ##fileName - string The path to file containing strings
    @staticmethod
    def readFile(markovDict, fileName):
        with open(fileName, "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                Markov.addSentenceToDict(markovDict, line)
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
            while curWord not in Markov._ENDPUNCTUATION:
                curWord = random.choices(list(markovDict[curWord][Markov._WORDS].keys()), weights=list(markovDict[curWord][Markov._WORDS].values()))[0]
                if(curWord not in string.punctuation and length > 0):
                    phrase += " "
                phrase += curWord
                length += 1
                
        else: #Chaos
            while curWord not in Markov._ENDPUNCTUATION:
                curWord = random.choice(list(markovDict[curWord][Markov._WORDS]))
                if(curWord not in string.punctuation and length > 0):
                    phrase += " "
                phrase += curWord
                length += 1
                
        return phrase, length

    #Prints out the dictionary sorted alphabettically along with the count of each word in detail
    ##markovDict     - Dictionary containing the words and counts
    #@staticmethod
    #def printDict(markovDict):
    #    for rootWord in sorted(markovDict):
    #        if rootWord == "":
    #            print("~STARTING~" + " - " + str(markovDict[rootWord][Markov._TOTAL]))
    #        else:
    #            print(rootWord + " - " + str(markovDict[rootWord][Markov._TOTAL]))
    #            
    #        for leafWord in sorted(markovDict[rootWord][Markov._WORDS]):
    #            if leafWord == "":
    #                print("~ENDING~" + " - " + str(markovDict[rootWord][Markov._WORDS][leafWord]))
    #            else:
    #                print("\t" + leafWord + " - " + str(markovDict[rootWord][Markov._WORDS][leafWord]))
    #            
    #        print(" ")
    #    return

    #@staticmethod
    #def testBasics(markovDict):
    #    #test file reading
    #    Markov.readFile(markovDict, "testFile2.txt")
    #    Markov.printDict(markovDict)
    #    
    #    #Test Json I/O
    #    Markov.save_json(markovDict)
    #    markovDict.clear()
    #    markovDict = Markov.load_json("TestMarkovChainData.txt")
    #    Markov.printDict(markovDict)
    #    
    #    #Test chain generation weighted vs unweighted
    #    print("Control\n---------------")
    #    for i in range(10):
    #        print(Markov.generateChain(markovDict, True))
    #    print("\n\nChaos\n---------------")
    #    for i in range(10):
    #        print(Markov.generateChain(markovDict, False))

