import json
import pickle
import random
import string
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
    async def load_json(path):
        try:
            with open(path,'r') as f:
                jsonObj = json.load(f)
                return jsonObj, True
        except (IOError, JSONDecodeError):
                return {}, False

    @staticmethod
    async def save_json(jsonObj, path):
        with open(path, 'w+') as f:
            json.dump(jsonObj, f)
            
    @staticmethod
    async def load_pickle(path):
        try:
            with open(path,'rb') as f:
                pickleObj = pickle.load(f)
                return pickleObj, True
        except (IOError, pickle.PickleError):
            return {}, False
            
    @staticmethod
    async def save_pickle(pickleObj, path):
        pickle.dump(pickleObj, open( path, "wb" ))
    
    #Adds a new word to the dictionary
    ##markovDict    - Dictionary to populate
    ##rootWord      - The initial word
    ##leafWord      - The word that comes after the rootWord
    @staticmethod
    async def addWordToDict(markovDict, rootOne, rootTwo, leafWord):
        if (rootOne, rootTwo) not in markovDict:
            markovDict[(rootOne, rootTwo)] = [0, {leafWord: 0}]
        if leafWord not in markovDict[(rootOne, rootTwo)][Markov._WORDS]:
            markovDict[(rootOne, rootTwo)][Markov._WORDS][leafWord] = 0
        markovDict[(rootOne, rootTwo)][Markov._TOTAL] += 1
        markovDict[(rootOne, rootTwo)][Markov._WORDS][leafWord] += 1
            
    #Adds a sentence to the dictionary
    ##markovDict    - Dictionary to populate
    ##sentence      - Sentence to be added to dictionary
    @staticmethod
    async def addSentenceToDict(markovDict, sentence):
        prevWord1 = ""
        prevWord2 = ""
        
        #Following line removes punctuation but it might be better to not remove it
        #sentence = sentence.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
        
        #Seperates all symbols and words
        #sentenceList = re.findall(r"[\w']+|[.,!?;]", sentence)
        
        for spaced in Markov._SYMBOLS:
            sentence = sentence.replace(spaced, ' {0} '.format(spaced))
        sentenceList = sentence.split()
        
        prevWord2 = sentenceList[0].lower()
        word = sentenceList[1].lower()
        
        await Markov.addWordToDict(markovDict, prevWord1, prevWord2, word)
        
        for i in range(0, len(sentenceList)):
            if len(sentenceList) > i+2:
                prevWord1 = sentenceList[i].lower()
                prevWord2 = sentenceList[i+1].lower()
                word = sentenceList[i+2].lower()
            
                await Markov.addWordToDict(markovDict, prevWord1, prevWord2, word)
            
        if(word not in string.punctuation):
            await Markov.addWordToDict(markovDict, prevWord2, word, ".")
            
            
    #Populates the dictionary from a file of strings
    ##markovDict     - Dictionary to populate
    ##fileName       - string The path to file containing strings
    @staticmethod
    async def readFile(markovDict, fileName):
        with open(fileName, "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                await Markov.addSentenceToDict(markovDict, line)
        return
        
    
    #Generates a phrase(chain) from the dictionary
    ##markovDict    - Dictionary containing the words and counts
    ##weighted      - Bool Whether a weighted probability based on occurance should be used
    @staticmethod
    async def generateChain(markovDict, weighted):
        phrase = ""
        curWord = ""
        length = 1
        
        startTuples = [key for key in list(markovDict.keys()) if key[0] == '']
        curTuple = random.choice(startTuples)
        phrase += curTuple[1]
        
        if weighted: #Control
            while curWord not in Markov._ENDPUNCTUATION and curTuple[1] != '' and length < 100:
                curWord = random.choices(list(markovDict[curTuple][1].keys()), weights=list(markovDict[curTuple][Markov._WORDS].values()))[0]
                if(curWord not in string.punctuation and length > 0):
                    phrase += " "
                phrase += curWord
                length += 1
                curTuple = (curTuple[1], curWord)
                
        else: #Chaos
            while curWord not in Markov._ENDPUNCTUATION:
                curWord = random.choice(list(markovDict[curTuple][1].keys()))
                if(curWord not in string.punctuation and length > 0):
                    phrase += " "
                phrase += curWord
                length += 1
                curTuple = (curTuple[1], curWord)
                
        return phrase, length
    
    ##Adds a new word to the dictionary
    ###markovDict    - Dictionary to populate
    ###rootWord      - The initial word
    ###leafWord      - The word that comes after the rootWord
    #@staticmethod
    #def addWordToDictOld(markovDict, rootWord, leafWord):
    #    if rootWord not in markovDict:
    #        markovDict[rootWord] = [0, {leafWord: 0}]
    #    if leafWord not in markovDict[rootWord][Markov._WORDS]:
    #        markovDict[rootWord][Markov._WORDS][leafWord] = 0
    #    markovDict[rootWord][Markov._TOTAL] += 1
    #    markovDict[rootWord][Markov._WORDS][leafWord] += 1
    #    
    #@staticmethod
    #def addSentenceToDictOld(markovDict, sentence):
    #    prevWord = ""
    #    
    #    #Following line removes punctuation but it might be better to not remove it
    #    #sentence = sentence.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    #    
    #    #Seperates all symbols and words
    #    #sentenceList = re.findall(r"[\w']+|[.,!?;]", sentence)
    #    
    #    for spaced in Markov._SYMBOLS:
    #        sentence = sentence.replace(spaced, ' {0} '.format(spaced))
    #    
    #    for word in sentence.split():
    #        word = word.lower()
    #        Markov.addWordToDict(markovDict, prevWord, word)
    #        prevWord = word
    #        if word in Markov._ENDPUNCTUATION:
    #            prevWord = "."
    #        
    #    if(prevWord not in string.punctuation):
    #        Markov.addWordToDict(markovDict, prevWord, ".")
    #        
    #        
    #        
    ##Generates a phrase(chain) from the dictionary
    ###markovDict    - Dictionary containing the words and counts
    ###weighted      - Bool Whether a weighted probability based on occurance should be used
    #@staticmethod
    #def generateChainOld(markovDict, weighted):
    #    phrase = ""
    #    curWord = ""
    #    length = 0
    #    
    #    if weighted: #Control
    #        while curWord not in Markov._ENDPUNCTUATION:
    #            curWord = random.choices(list(markovDict[curWord][Markov._WORDS].keys()), weights=list(markovDict[curWord][Markov._WORDS].values()))[0]
    #            if(curWord not in string.punctuation and length > 0):
    #                phrase += " "
    #            phrase += curWord
    #            length += 1
    #            
    #    else: #Chaos
    #        while curWord not in Markov._ENDPUNCTUATION:
    #            curWord = random.choice(list(markovDict[curWord][Markov._WORDS]))
    #            if(curWord not in string.punctuation and length > 0):
    #                phrase += " "
    #            phrase += curWord
    #            length += 1
    #            
    #    return phrase, length
        
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

