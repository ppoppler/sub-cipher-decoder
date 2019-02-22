
import math

"""
NGramScore Class, a class that generates a score based on the type of file inserted
The files must contain text and the values(frequencies) of each text immediately afterwards

Generate score generates a score based on the entire text and given the information in the text file 

NGramScore and the textfiles are based on: http://practicalcryptography.com/cryptanalysis/text-characterisation/quadgrams/#a-python-implementation

"""
class NGramScore(object):
    """
    Constructor: The file the chosen determines what kind of
    ngram is made (bigram, trigram, quadgram, etc.)
    """
    ngrams = {}
    def __init__(self,nfile,sep=' '):
        #Create an empty dictionary
        self.ngrams = {}
        #open file
        f = open(nfile,'r') 
        for line in f:
            key,count = line.split(sep)
            self.ngrams[key] = int(count)
        #Create Length
        self.Length = len(key)
        #Create Count
        self.Count = sum(iter(self.ngrams.values()))
        #Calculate the probabilities for each key in ngrams
        for key in self.ngrams.keys():
            self.ngrams[key] = math.log10(float(self.ngrams[key])/self.Count)
        #Create a score to default on if there isn't an ngram
        self.Floor = math.log10(0.01/self.Count)

    """
    Given the score of a text excerpt, generate a score.
    For the sake of the comments, I use "quadgrams" instead of ngrams
    Any time of ngram can be inserted with this score generator (bigrams,trigrams, etc.)
    """
    def GenerateScore(self,text):
        #assuming the text has whitespace and lowercase letters
        #the text needs to be matched with the quadgrams which are all uppercase
        text = text.replace(" ","").upper()
        #score is initially set to zero
        score = 0
        ngram = self.ngrams.__getitem__
        #for x in the of 0 to the length of text minus the length of key
        for x in range(len(text)-self.Length+1):
            #if the quadgram is in ngrams
            if text[x:x+self.Length] in self.ngrams:
                #add that quadgrams value to the score
                score += ngram(text[x:x+self.Length])
            else:
                #otherwise add the floor
                score += self.Floor
        #return score
        return score
    #end of GenerateScore


