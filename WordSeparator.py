import math
import os
"""
Class that calls the insert_spaces
function with inserts spaces in between words that are combined together (theapple => the apple)
Based off of code used from https://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words  on 10/7/2018
(also implemented as wordninja here: https://pypi.org/project/wordninja/)

Modification of the code include: creating a class and constructor to run spacing algorithm
Modifying some of the names within insert_spaces
"""

INITIAL_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

class WordSeparator(object):

    #Constructor that initializes with the wordlist from words_sorted.txt
    def __init__(self):
        #Read the entire list and split the text
        self.wordlist = open(INITIAL_FILE_PATH + "\\words_sorted.txt").read().split()
        #Create a dictionary where the key is the word, and the value of the word is based off of the log of the current
        #index multiplied by the length of the entire list of words, meaning the larger the value 
        self.wordvalues = dict((k,math.log((j+1)*math.log(len(self.wordlist)))) for j,k in enumerate(self.wordlist))
        self.maxwords = max(len(x) for x in self.wordlist)
       
    """
    Adds spaces within a text of words without spaces between them.
    @param text: text to have spaces added to 
    """
    def insert_spaces(self,text):

        #Function that finds the match for the i first characters
        #if there is a cost for the first i-1 characters
        def match(i):
            #values equal equal to a reversed iterator through all of the costs
            values = enumerate(reversed(cost[max(0,i-self.maxwords):i]))
            #return the minimum of 
            return min((c + self.wordvalues.get(text[i-k-1:i],9e999),k+1) for k,c in values)
        
        #initialize cost
        cost = [0]
        #for each letter in the text
        for i in range(1,len(text)+1):
            #get the matches
            c,k = match(i)
            #append c to the cost
            cost.append(c)
        
        #Create output list
        out = []
        #i equal to the length of the entire text
        i = len(text)
        #while i greater than zero (backwards loop)
        while i>0:
            #match starting backwards
            c,k = match(i)
            #assert an exception if c doesn't eequal the cost of [i]
            assert c == cost[i]
            #add that word to the out dictionary
            out.append(text[i-k:i])
            #decrement the loop counter
            i -=k
        #afterwards, out will be a list of all the words in reversed order. reverse it again to have the text in correct
        #order as a list, and return as a string
        return " ".join(reversed(out))
