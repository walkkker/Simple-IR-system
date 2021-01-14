import collections
import re
from stemming.porter2 import stem

def tokenization(content):
	#delete "'" from the punctuation set, because in the stop words file, some stop words invlove '.
		word_tokens = re.sub(r'[!@#$%^&*()_+{}|:"<>?,./;\'[\]\-=]+', ' ', content).lower().split()
		return word_tokens

def stop_words(word_tokens):
	with open('englishST.txt', 'r') as f:
		content = f.read()
	stop_word_tokens = tokenization(content)
	filter_stop = [w for w in word_tokens if w not in stop_word_tokens]
	return filter_stop

def porter_stemmer(filter_stop):
	filter_stemmer = [stem(tokens) for tokens in filter_stop]
	return filter_stemmer

def pre_processing(content):
	word_tokens = tokenization(content)
	filter_stop = stop_words(word_tokens)
	filter_stemmer = porter_stemmer(filter_stop)
	return filter_stemmer


