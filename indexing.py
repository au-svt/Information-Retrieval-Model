from bs4 import BeautifulSoup
# import nltk
import string
from nltk.tokenize import word_tokenize
from collections import Counter
import math
import numpy
import json
import os
import sys
import pickle

def extract(filename = ''):
    '''
    returns 
    title_list: where title_list[i] is title of ith document in the file(say in wiki_00)
    and
    doc_list: where doc_list[i] is complete parsed text of ith document  
    '''
    file = open(filename, 'r')
    soup = BeautifulSoup(file, features="html.parser")
    docs=soup.findAll("doc")	# each document is present in <doc id=.. title=..> and </doc>
    title_list = []
    title_list=[x["title"] for x in docs]
    doc_list = [BeautifulSoup(str(doc), features="html.parser").get_text() for doc in docs]
    return doc_list,title_list


def pre_processing(text):
    '''
    input: list of raw text(parsed by html parser in our case). 
           text[i] is raw text of ith document 
    output: tokens[i] is a list of complete ith document,
            tokens[i][j] is jth token of ith document (and ofcourse: no check on repeating words)
    '''
    tokens = []
    punc = [w for w in string.punctuation if not (w=='\'' or w=='-' or w=='%' or w==':')]	# to remove all standard punctuations except '-', etc
    punc = ''.join(punc)
    table = str.maketrans('', '', punc)	# table which maps each punctuation(which we want to remove) to None. Thus to replace them with None in text
    for doc in text:
        token_doc = word_tokenize(doc)	# list of string tokens for a document
        token_doc = [w.translate(table) for w in token_doc]	# remove punctuations
        token_doc = [x.lower() for x in token_doc]	# lower case satndardisation
        token_doc = [w for w in token_doc if not (w=="''" or w=='' or w=="' '")]	# remove space or empty quote tokens
        tokens.append(token_doc)
        # print(token_doc)
    return tokens



def get_unigrams(text):
    '''
    input: list of (list of tokens)
    output: list of dictionaries keeping tf count per document
    unigram[0]['the']=607 // 0th doc contains 'the' 607 times
    '''
    unigrams = [Counter(doc) for doc in text] # doc is 1 document , text conain 450-ish docs
    # counter creates dictionary for every document, with key: a term in that document, and value: tf in the document
    # unigrams is list of such dictionaries 
    return unigrams


def get_inverted_index(freq_list):
    #create set from list of tokenized docs    
    '''
    input: list of dictionaries for each document, keeping tf(t,d) count
    outputs: a dictionary with keys:each unique term in the corpus, and value: list of their frequency count in various documents(id)
    '''
    inverted_index = {}
    for i in range(len(freq_list)): # number of documents
        doc = freq_list[i]
        for key in doc.keys():
            if key in inverted_index.keys():
                inverted_index[key].append((i, doc[key]))	# if not a new word, then append in the 'dictionary value' that is a list
                						# doc[key] is tf(t,d), i.e. no of frequency of 'key' in the document 'doc'
            else:
                inverted_index[key] = []
                inverted_index[key].append((i, doc[key]))	# if a new word, first create a new list and then append in it 

    return inverted_index





def main(argv1, argv2):
    # command line arguments are both optional combined(either both are there or none). If none, then default strings are given input
    # arg1 is suppoesd to contain local path of corpus file. example 'AA/wiki_00' (will be changed to take absolute path of corpus)
    # arg2 is supposed to contain name of the directory that will be created(if not present) to store the inverted index, frequency list, and title list describing the corpus
    # default arg1 : AA/wiki_00 
    # default arg2 : indexFiles
    
    #filepath = '/media/ponyket/New Volume/dcpp_downloads/'
    filepath = './'
    
    filename = filepath + argv1 	# argv should be : 'AA/wiki_00'
    list_of_documents,title_list = extract(filename)	# list_of_documents: where list_of_documents[i] is complete parsed text of ith document
    processed_text = pre_processing(list_of_documents) # processed_text[i] is a list of complete ith document tokens,
            						 # processed_text[i][j] is jth token of ith document (and ofcourse: no check on repeating words)
    freq = get_unigrams(processed_text) #Stores document-wise frequency of unigrams (a list of dictionary) 
    					 # this is also called as freq_list
    inverted_index = get_inverted_index(freq) # complete inverted index dictionary with frequencies in a document is stored along with document id ex: 'the':[ (1,100), (2,250), ..]

    
    if not os.path.exists(arg2):	# create the directory if not exists
        os.makedirs(arg2)
    
    '''
    list_of_documents = []
    title_list = []
    processed_text = []
    freq = []
    
    '''
    # write all the lists and dictioaries in 3 separate files in the folder argv2 (probably 'indexFiles') 
    with open(argv2+'/inverted_index_dict.json', 'w') as f:
        json.dump(inverted_index, f)
    print('...created and Stored inverted_index_dict.json ...')
    
    with open(argv2+'/freq_list.json', 'w') as f:
        json.dump(freq, f)
    print('...created and Stored freq_list.json ...')
    
    with open(argv2+'/title_list_file.json', 'w') as f:
        json.dump(title_list, f)
    print('...created and Stored title_list_file.json ...\nCompleted!')
    
    ## this is the hardcoded version
    
    dict = {}
    dict['me'] =  ['me', 'me-and', 'myself']
    dict['enlighten'] =  ['enlighten', 'expound', 'inspire']
    dict['viral'] = ['viral', 'virus', 'infection'] 
    dict['foreigner'] = ['foreigner', 'foreigners', 'nationality']
    dict['main'] = ['main', 'main-sequence', "'main"]
    dict['poverty'] = ['poverty', 'poverty…by','inequality' ]
    dict['of'] = ['of', "'of", 'the']
    dict['cause'] = ['cause', 'causes', 'causing']
    
    
    # import pickle
    with open(argv2+ '/relatedWords.pickle', 'wb') as f:
        pickle.dump(dict, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    #with open('relatedWords.pickle', 'rb') as f:
    #    d = pickle.load(f)

    
    


if __name__ == "__main__":
    try:
        # print('trying\n')
        arg1 = sys.argv[1]
        
    except:
        arg1 = 'AA/wiki_00'
	    
    try:
        arg2 = sys.argv[2]
    except:
        arg2 = './indexFiles'
    
    # command line arguments are both optional combined(either both are there or none). If none, then default strings are given input
    # arg1 is suppoesd to contain local path of corpus file. example 'AA/wiki_00' (will be changed to take absolute path of corpus)
    # arg2 is supposed to contain name of the directory that will be created(if not present) to store the inverted index, frequency list, and title list describing the corpus
    # default arg1 : AA/wiki_00 
    # default arg2 : indexFiles
    
    print('Input file: ',arg1,'\nOutput folder: ',arg2)
    main(arg1, arg2)









