import os
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.conf import settings


import nltk
nltk.download('stopwords')
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import requests
from owlready2 import *
import types
import spacy
from django.middleware.csrf import get_token


ps = PorterStemmer()

data = []
fin_data = []
sent = []
score = []
ontology = []


class Token:
	def __init__(self, text=None,dep=None,head_text=None,head_pos=None,children=None):
		self.text = text
		self.dep = dep
		self.head_text = head_text
		self.head_pos = head_pos
		self.children = children

def index(request):
	csrf_token = get_token(request)
	return render(request,'index.html',{'csrf_token':str(csrf_token)})

def summarize(request):
	global data
	csrf_token = get_token(request)
	print("summarize")
	if request.is_ajax():
		request_data = request.POST
		data = [request_data['input_text']]

		result = giveresult()
		return JsonResponse(result)


def giveresult():
	# csrf_token = get_token(request)
	global data
	global fin_data
	global sent
	global score
	global ontology
	if data:
		sample_text = str(data[0]).strip()
		fin_data = summary(sample_text)
		sent = []
		score = []
		varname = 'testing.owl'
		f = open(varname, "r").read()
		ontology = [f]
		for item in fin_data:
			sent.append(item[0])
			score.append(item[1])

		sent.reverse()
		score.reverse()

	temp = {'ontology':ontology,'data':data,'sent':sent,'score':score}

	return temp


def RemPunc(string):
    punctuations = '''!()‘’-[]{};:'"\,<>./?@#$%^&*_~\n“”'''
    for char in string:
        if char in punctuations:
            string = string.replace(char," ")
    return string.strip()



def summary(sample_text):
	sample_text = sample_text.lower().strip()

	custom_sent_tokenizer = PunktSentenceTokenizer(sample_text)
	tokenized_sent = custom_sent_tokenizer.tokenize(sample_text)

	nlp = spacy.load("en_core_web_sm")
	token_arr = {}
	stop_words = set(stopwords.words("english"))
	punctuations = '''!()‘’-[]{};:'"\,<>./?@#$%^&*_~\n “”'''

	for sent in tokenized_sent:
		doc = nlp(sent)
		for token in doc:
			if str(token) not in punctuations:
				chii = [str(child) for child in token.children]
				chi = []
				for item in chii:
					if item not in punctuations:
						chi.append(item)
				temp = Token(token.text, token.dep_, token.head.text, token.head.pos_,chi)
				token_arr[token.head.text] = temp

	adj_list = {}
	for item in token_arr:
	    if str(item) in adj_list.keys():
	        if adj_list[item].dep == token_arr[item].dep:
	            adj_list[item].children=token_arr[item].children+ adj_list[item].children
	    else:
	        adj_list[item]=token_arr[item]

	onto = get_ontology("http://test.org/onto.owl")
	with onto:
	    class N_Token(Thing):
	        pass

	for item in adj_list:
	    try:
	        class_lst = list(onto.classes())
	        node_dict = {}
	        for cl in class_lst:
	            node_dict[str(cl)] = cl
	        if str('onto.'+adj_list[item].text) not in list(node_dict.keys()):
	            NewClass = type(adj_list[item].text, (N_Token,), { 
	            })   
	        class_lst = list(onto.classes())
	        node_dict = {}
	        for cl in class_lst:
	            node_dict[str(cl)] = cl

	        if adj_list[item].children:
	            for chi in adj_list[item].children:

	                NewClass = type(chi, (node_dict[str('onto.'+ str(adj_list[item].text))],), { 
	                })
	    except:
	        print("done")

	onto_path.append("")
	onto.save()
	onto.save(file = "testing.owl", format = "rdfxml")

	fin_arr = []
	for item in adj_list.keys():
	    fin_arr.append([item]+list(adj_list[item].children))
	stop_words = set(stopwords.words("english"))

	sent_score = {}
	for arr in fin_arr:
	    for k in arr:
	        sent_score[k] = 0

	for sent in tokenized_sent:
	    for tok in str(RemPunc(str(sent))).split(" "):
	        if tok not in stop_words:
	            for arr in fin_arr:
	                if tok in arr:
	                    if str(arr[0]) not in stop_words:
	                        sent_score[str(arr[0])] +=1
	                    sent_score[tok] +=1
	        else:
	            for a in fin_arr:
	                if tok in a:
	                    if a.index(tok) == 0:
	                        for ele in a:
	                            if ele not in stop_words:
	                                sent_score[ele] +=1

	final_score = []
	for sent in tokenized_sent:
	    temp = 0
	    for tok in str(RemPunc(str(sent))).split(" "):
	        if tok in sent_score.keys():
	            temp += sent_score[tok]
	    final_score.append(temp)

	sent_dict = {}

	for ele in range(len(final_score)):
	    sent_dict[final_score[ele]] = tokenized_sent[ele]

	sentt_dict = sorted(sent_dict.keys())

	sorted_dictt = {}

	for item in sentt_dict:
	    sorted_dictt[sent_dict[item]] = item
	
	k = list(sorted_dictt.items())

	return k





