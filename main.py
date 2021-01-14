from inverted_index_improved import extract_xml_file, positional_inverted_index
from search import *
from tfidf import tfidf_retrieval, tfidf_process
import re


if __name__ == '__main__':

	inverted_index = positional_inverted_index()
	
	with open("queries.boolean.txt", "r") as query_file:
		for query in query_file.readlines():
			print(query)
			if re.fullmatch(r'\w+\s"\w+\s\w+"', query.strip(), re.DOTALL):
				phrase_search(query.strip(), inverted_index)
			elif re.fullmatch(r"\w+\s#\d+\(\w+,\s?\w+\)", query.strip(), re.DOTALL):
				proximity_search(query.strip(), inverted_index)
			elif re.fullmatch(r'\w+\s"\w+\s\w+"\s[A-Z]+(\s[A-Z]+)?\s\w+\b', query.strip(), re.DOTALL):
				phrase_boolean_term(query.strip(), inverted_index)
			elif re.fullmatch(r"\w+\s\w+\s[A-Z]+(\s[A-Z]+)?\s\w+", query.strip(), re.DOTALL):
				term_boolean_term(query.strip(), inverted_index)
			elif re.fullmatch(r'\w+\s"\w+\s\w+"\s[A-Z]+(\s[A-Z]+)?\s"\w+\s\w+"', query.strip(), re.DOTALL):
				phrase_boolean_phrase(query.strip(), inverted_index)
			elif re.fullmatch(r"\w+\s(\w+)", query.strip(), re.DOTALL):
				single_term_search(query.strip(), inverted_index)
			else:
				print("wrong request or format!")

	tfidf = tfidf_process(inverted_index)

	with open("queries.ranked.txt", "r") as query_file:
		for ranked_query in query_file.readlines():
			tfidf_retrieval(ranked_query, tfidf)


	