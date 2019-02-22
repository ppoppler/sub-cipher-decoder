import pprint
import collections
#important import using pyenchant at: https://pypi.org/project/pyenchant/ 
from enchant.checker import SpellChecker
import random
import importlib
from NGramScore import NGramScore
import WordSeparator
import os 

"""
*************IMPORTANT*************

All the text files are assumed are read from the same directory as CECS 378 Lab 1.py
All additional python files are also supposed to be imported from the same directory as CECS 378 Lab 1.py
pyenchant (enchant) also needed to run thet code


Examples of the output and their correct answers are provided in output examples.txt

***********************************
"""


INITIAL_FILE_PATH = os.path.dirname(os.path.realpath(__file__))


"""
Cesar Decoder
Decodes a cesar cipher by providing all the combinations
and then finding the combination with the least spelling errors,
granting the actual plaintext
@param message: ciphertext to be decoded
"""
def cesar_decoder(message):
    #base string s, stringlist array
    s = ""
    stringlist = []
    #alphabet for the base key 
    alpha = list("abcdefghijklmnopqrstuvwxyz")
    #orig_key = ciphertext with lowercase, no spaces
    orig_key = list(message.lower().replace(" ",""))
    #Below for statement creates the 26 different cesar ciphers that can be found
    for shift in range(1,26):
        #list message is to lower
        listmessage = list(message.lower())
        #for x in the range of list message
        for x in range (0,len(listmessage)):
            #ignore all spaces
            if(listmessage[x] != chr(32)):
                #shift all the letters a certain amount of indexes (x)
                y = chr((ord(listmessage[x])+shift))
                if y > chr(122):
                    y = chr(ord(y)%122 + 96)
                listmessage[x] = y
            elif(listmessage[x] == chr(32)):
                listmessage[x] = ""
        #afterwards save the listmessage as s
        s = "".join(listmessage)
        #append s to all the cesar shifts in stringlist
        stringlist.append(s)
    
    #initially, key is not found
    keyFound = False
    #the key will start out originally as the alphabet
    key = alpha
    #create a word separator to split the cesar shifts of the cipher text to 
    #see if they are in english
    separator = WordSeparator.WordSeparator()
    #for each string (cesar cipher shift) in the stringlist 
    for strng in stringlist:
        #insert the spaces to the string. if it's jibberish, it will have hard time adding spaces.
        st = separator.insert_spaces(strng)
        #create a spellchecker using enchant for the string
        checker = SpellChecker("en_US",st)
        error =0
        #Count all the errors in the shift string
        for err in checker:
            error+=1
        #If there's barely any errors, odds are that it's in english
        if error <2:
            #key is now found
            keyFound = True
            s = st
            #create a key dict to set the original alphabet to the new key
            keydict = {}
            for x in range(0,len(orig_key)):
                keydict[orig_key[x]] = strng[x]
            #then fixed key in a list
            for k,v in keydict.items():
                index = alpha.index(k)
                key[index] = v
            break

    #if the key is found, print it out 
    if(keyFound):
        #plaintext
        print(s)
        #alphabet
        print("Base key:", list("abcdefghijklmnopqrstuvwxyz"))
        #key (If there are duplicates in letters, odds are that those letters aren't used in the plaintext or ciphertext))
        #For example if 'e' in alphabet matches with 'e' in the key, then they are NOT a key for each other.
        #if 'f' in the alphabet matches with 'e' in the key, then e is the substitute for 'f'.
        print("Actual key:", key)


        
"""
Find indexes is a helper function that returns all of the indexes where
a character appears within a string
"""
def find_indexes(s,ch):
    #enumerate through the string and return a list of all the indexes that contain that letter
    return [i for i, letter in enumerate(s) if letter == ch]

"""
Decipher is a helper method that takes in a key and substitutes all the letters in a given string
With other letters. Essentially performs a substitution cipher on a string.
"""
def decipher(key, text):
    #Alphabetical key
    startkey = list('abcdefghijklmnopqrstuvwxyz')
    #Replace all the whitespace
    text = text.replace(" ","")
    #Turn text into a list
    t = list(text)
    #For x in the range of the alphabetical key
    for x in range(0,len(startkey)):
        #Find all of the indexes within the text and replace them with them with each letter for the alphabet
        indexes = find_indexes(text,startkey[x])
        #replace all of the indexes of the test with the key 
        for index in indexes:
            t[index]=key[x]
    #turn text into a string then return
    text = "".join(t)
    return text

"""
Substitution Decoder deciphers a substitution cipher and provides the plaintext.
Using quadgrams and trigrams to calculate scores, larger scores are generate through randomly generate keys
until a stronger score is found. Each new base score comes with errors.

A base score is strong enough when it has fewer than 5 errors. When that occurs, the program stops shuffling
the key and specifically downsizes the problem to find the correct answer. By using a smaller sample size
(using the letters in the error words), the program tries to substitute these letters to fix the errors and
provide a correct answer

@param ptext: the ciphertext to be decoded
@param maxerrors: the maximum number of errors 


Dependencies:

Pyenchant (aka enchant) used to for spellchecker

english_quadgrams.txt and english_trigrams.txt are files containing quadgrams and trigrams and there respective frequencies
Used to calculate the scores. 

Found via: 
http://practicalcryptography.com/cryptanalysis/text-characterisation/quadgrams/#a-python-implementation


"""
def substitution_decoder(ptext,maxerrors):
    #rating 1 reads from the quadgrams file
    rating = NGramScore(INITIAL_FILE_PATH + '\\english_quadgrams.txt')
    #rating 2 reads from the trigrams file
    rating1 = NGramScore(INITIAL_FILE_PATH + '\\english_trigrams.txt')
    #lastkey initialized as a list of the alphabet. Is gradually updated when the 
    lastkey = list('abcdefghijklmnopqrstuvwxyz')
    #maxscore is initailized as a extremely large negative number
    maxscore = -99e9
    #parentscore is initialzied as maxscore, meant to be updated immediately by another key's score
    #and continually updated when a better score is found 
    parentscore = maxscore
    #basekey is initialized as the lastkey, updated whenever a better key is found
    basekey = lastkey[:]
    #parrenterrors is initialized as an extremely large positive number, meant to reduced whenever better keys are found 
    parenterrors = 99e9
    #finalizedkey is a specific subset of basekey which is only updated whenever the key is close to finishing
    finalizedkey = basekey[:]
    #boolean that keeps the program running until the answer is found
    answerNotFound = True
    #boolean that indicates whether or not the program is close to finding the correct ciphertext
    close = False
    #innerset is a list of all the letter contained within all error words. It is initially empty
    #but use when close = True. The letters are used to substitute for random letters in the alphabet
    innerset = []
    #initialized variable
    i = 0

    #Program starts... while the answer hasn't been found:
    while(answerNotFound):
        i+=1
        #If the key isn't close:
        if close == False:
            #shuffle the key
            random.shuffle(basekey)
        #Decipher the message given the basekey and the ciphertext
        subbed_message = decipher(basekey,ptext)
        #Generate the parent score given the trigrams and quadgrams
        parentscore =  rating.GenerateScore(subbed_message) + rating1.GenerateScore(subbed_message) #+ rating2.GenerateScore(subbed_message)
        
        #Count initialized at 0 
        count = 0
        #If the key isn't close:
        if close == False:
            #perform 1000 swaps 
            while count < 1000:
                #generate two random numbers
                a = random.randint(0,25)
                b = random.randint(0,25)
                #child will equal the basekey 
                child = basekey[:]
                #swap the keys within the basekey
                child[a],child[b] = child[b],child[a]
                #decipher the child text 
                subbed_message = decipher(child, ptext)
                #generate a score for the deciphered text for the child
                score = rating.GenerateScore(subbed_message) + rating1.GenerateScore(subbed_message) #+ rating2.GenerateScore(subbed_message)

                #if the child's score is better than the parent's score:
                if score>parentscore:
                    #set the parent's score equal to the child's score
                    parentscore = score
                    #set the basekey equal to the child key 
                    basekey = child[:]
                    #reset the swap counter
                    count = 0
                #increment swap counter
                count+=1 
        
        #if the key is close:
        if close == True:
            #choose a random index from the innerset, the set of letters from error words
            a = random.choice(innerset)
            #choose a random number to swap with the error letter
            b = random.randint(0,25)
            #child key equals basekey
            child = basekey[:]
            #swap the two letters
            child[a],child[b] = child[b],child[a]
            #decipher using the new child key 
            subbed_message = decipher(child, ptext)
            #generate a new score for the child key 
            score = rating.GenerateScore(subbed_message) + rating1.GenerateScore(subbed_message) #+ rating2.GenerateScore(subbed_message)
            #save the key as a finalizedkey, to be used in a separate process
            finalizedkey = child[:]
        
        #if the parentscore is good and the maxscore isn't close 
        if parentscore>maxscore and close == False:
            #lastkey equals the basekey
            lkey = basekey[:]
            #create a word separator
            separator = WordSeparator.WordSeparator()
            #separate the words
            cracked = separator.insert_spaces(decipher(lkey,ptext))
            #create a spell checker using cracked as the text
            checker = SpellChecker("en_US",cracked)
            #initially start with zero errors
            errors = 0
            errorwords = []
            
            #record and print all the errors
            for err in checker:
                print ("ERROR:", err.word)
                errorwords.append(err.word)
                errors+=1
            #if the current amount of errors is less than the parent's amount of errors:
            if errors < parenterrors:    
                #set the parent's amount of errors equal to current amount of errors
                parenterrors = errors
            #if there are less than five errors in the parent's errors
            if parenterrors <= 5:
                #set close to True; program almost to the correct answer
                close = True
                #notify
                print("Close to final answer...")
                #for each error in errorwords:
                for err in errorwords:
                    #turn each error (string) to a list
                    errl = list(err)
                    #for each letter in the list
                    for e in errl:
                        #append it to the innerset
                        innerset.append(basekey.index(e))
                #remove duplicates by making it into a set
                innerset = set(innerset)
                #put it back to a list
                innerset = list(innerset)
                #printing the innerset
                print(innerset)

            #set the maxscore and lastkey equal to the parentscore and basekey, respectively    
            maxscore,lastkey = parentscore,basekey[:]
            
            #if there are less errors than require amount of max errors:
            if errors <= maxerrors:
                #Then its the final iteration, print out the final iteration
                print("Final Iteration")
                #Change the boolean (answer is found)
                answerNotFound=False
                #Print iteration
                print('Iteration',i)
                #Print the key
                print('Best key: ', lastkey)
                #Print the plaintext, with spaces for simplicity
                print('Plain text: ', separator.insert_spaces(decipher(lastkey,ptext)))
                #print the score
                print(parentscore)
            #Otherwise print regular information, just iteration, key, and plaintext all jumbled
            else:
                print('Iteration',i)
                print('Best key: ', lastkey)
                print('Plain text: ', decipher(lastkey,ptext))
                print(parentscore)

        #If close is true
        if close == True:
            #last key equals the finalized key
            lkey = finalizedkey[:]
            #create a word separator
            separator = WordSeparator.WordSeparator()
            #using the word separator, insert spaces into the text with the finalized key (lkey)
            cracked = separator.insert_spaces(decipher(lkey,ptext))
            #create a spell checker for the spaced out text 
            checker = SpellChecker("en_US",cracked)
            #Initialize errors
            errors = 0
            #Find all the errors
            for err in checker:
                #print ("ERROR:", err.word)
                errors+=1
            #If there are less errors than the parent errors
            if errors < parenterrors:
                #Change the scores, but more importantly change the keys. Finalized key will be more specific
                #than lastkey
                maxscore,lastkey = parentscore,finalizedkey[:]
                #If the errors are less than the required amount of minimum errors:
                if errors <= maxerrors:
                    #Print out all therrors
                    for err in checker:
                        print("ERROR:", err.word)
                    #Notify user of the final iteration
                    print("Final Iteration")
                    #Set answerNotFound to True (answer found)
                    answerNotFound=False

                #Print out of the information
                print('Iteration',i)
                print('Base: ', list("abcdefghijklmnopqrstuvwxyz"))
                print('Best key: ', lastkey)
                print('Plain text: ', separator.insert_spaces(decipher(lastkey,ptext)))
                print(parentscore)

"""
Randomy encrypts a given message

"""
def encrypt_substitution(m):
    
    #save original message
    original = m
    #lowercase message and reaplce all the periods, etc.
    m = m.lower()
    m = m.replace(";","")
    m = m.replace("-","")
    m = m.replace(" ","")
    m = m.replace(".","")
    m = m.replace(",","")
    #Create the key arrays for a future dictionary displaying the key.
    #key1 is the original letters
    key1 = list("abcdefghijklmnopqrstuvwxyz")
    #key2 is the keys of the encrypted letters
    key2 = []
    #Print out instructions for the user
    print("Now input the key based on the following letters in the phrase. Do not use repeats.")
    print("Key should be 26 characters long and based of the alphabet: abcdefghijklmnopqrstuvwxyz")
    #Invalid key initially true
    invalidKey=True
    while (invalidKey):
        #Second (actual) key is inputted by the user
        key2 = input()
        #for each letter in original key
        for x in key1:
            #find the amount indexes of letters appearing in the new key
            indexes = len(find_indexes(key2,x))
            #if there are multiples of the same letter or the size is different than the original (26):
            if(indexes>1 or len(key2)!=len("abcdefghijklmnopqrstuvwxyz")):
                #Then its invalid, and keep going
                print("Invalid response, do not use duplicate letters or non alphabetical characters.")
                invalidKey = True
                break
            else:
                #Otherwise, leave the while loop once done with the forloop. The key is valid.
                invalidKey = False

    #Create the key dictionary
    key = dict()
    key2=list(key2)
    for i in range(0,len(key2)):
        #append all the keys
        key[key1[i]]=key2[i]

    #Swap all of the keys
    encryptedMessage = list(m)
    for letter in key.keys():
        indexes = find_indexes(m,letter)
        for index in indexes:
            encryptedMessage[index] = key[letter]
    encryptedMessage = "".join(encryptedMessage) 
    print("Original Message: \n",m)
    print("Encrypted message: \n",encryptedMessage)
    print("Key: Original:Encrypted \n",key)
    

    

def main():
    #Main menu options
    print("CECS 378 Lab 1")
    print("Choose from the following options")
    print("1. Decrypt #1 (Cesar)")
    print("2. Decrypt #2 (Cesar)")
    print("3. Decrypt #3 (Substitution)")
    print("4. Decrypt #4 (Substitution)")
    print("5. Encrypt #1")
    print("6. Encrypt #2")
    print("7. Encrypt #3")
    userinput = int(input("Enter an option: "))
    if(userinput==1): #Option 1, Cesar cipher 
        cesar_decoder("fqjcb rwjwj vnjax bnkhj whxcq nawjv nfxdu mbvnu ujbbf nnc")
    elif(userinput==2): #Option 2, Cesar cipher
        cesar_decoder("oczmz vmzor jocdi bnojv dhvod igdaz admno ojbzo rcvot jprvi oviyv aozmo cvooj ziejt dojig toczrdnzno jahvi fdiyv xcdzq zoczn zxjiy")
    elif(userinput==3):  #Option 3, Substitution, Option sometimes works, sometimes gets stuck. Runtime can very drastically
        substitution_decoder("ejitp spawa qleji taiul rtwll rflrl laoat wsqqj atgac kthls iraoa twlpl qjatw jufrh lhuts qataq itats aittkstqfj cae",3)
    elif(userinput==4): #Option 4, Substitution, Option works well but sometimes slow
        substitution_decoder("iyhqz ewqin azqej shayz niqbe aheum hnmnj jaqii yuexq ayqkn jbeuq iihed yzhni ifnun sayiz yudhesqshu qesqa iluym qkque aqaqm oejjs hqzyu jdzqa diesh niznj jayzy uiqhq vayzq shsnj jejjz nshnahnmyt isnae sqfun dqzew qiead zevqi zhnjq shqze udqai jrmtq uishq ifnun siiqa suoij qqfni syyle iszhnbhmei squih nimnx hsead shqmr udquq uaqeu iisqe jshnj oihyy snaxs hqihe lsilu ymhni tyz",2)
    elif(userinput==5): #Option 5, Encryption via Substitution
        encrypt_substitution("He who fights with monsters should look to it that he himself does not become a monster. And if yougaze long into an abyss, the abyss also gazes into you")
    elif(userinput==6): #Option 6, Encryption via Substitution
        encrypt_substitution("There is a theory which states that if ever anybody discovers exactly what the Universe is for and whyit is here, it will instantly disappear and be replaced by something even more bizarre and inexplicable.There is another theory which states that this has already happened.")
    elif(userinput==7): #Option 7, Encryption via Substitution
        encrypt_substitution("Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in mysoul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear ofevery funeral I meet; and especially whenever my hypos get such an upper hand of me, that it requiresa strong moral principle to prevent me from deliberately stepping into the street, and methodicallyknocking people’s hats off - then, I account it high time to get to sea as soon as I can.")
    
main()

