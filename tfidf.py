import math
from preprocessing import pre_processing
from inverted_index_improved import extract_xml_file
import re

def tfidf_process(inverted_index):
	N = 5000  #total number of documents
	tfidf = {}
	file_info = {}

	xml_content = extract_xml_file("trec.5000.xml")
	for single_file in xml_content:
	# headline + text   format of file_info: [(docid, [tokens of headline + text]),(),(),(),()]
		file_tokens= pre_processing(single_file[1]) + pre_processing(single_file[2])
		file_info[single_file[0]] = file_tokens

	# calculate tfidf
	for term in inverted_index.keys(): # inverted_index[term] len(inverted_index[term]) is the length
			idf_part = math.log(N/len(inverted_index[term]), 10)
			tfidf[term] = {}
			for term_doc in inverted_index[term]: # term_doc[0]: docid  term_doc[1] list of positions  tr: len(term_doc[1])/len(file_info[term_doc[0]])
				tf_part = 1 + math.log(len(term_doc[1]), 10)
#N/len(inverted_index[term])  idf: math.log(N/len(inverted_index[term]), 10)
#w(t.d) = tf_part*idf_part
				tfidf[term][term_doc[0]] = tf_part * idf_part
	return tfidf


def tfidf_retrieval(ranked_query, tfidf):

	query_info = re.findall(r"(\d+)\s([\sA-Za-z]+)", ranked_query, re.DOTALL)

	serial_number = query_info[0][0]
	query_content = query_info[0][1]
	query = pre_processing(query_content)
	
	term_doc_list = []
	#this part is designed to process the input
	for query_term in query: #Get a list of docid involing any number of terms of the query
		term_doc_list += tfidf[query_term].keys()
	
	doc_result = list(set(term_doc_list))
	docid_score_list = []
	for docid in doc_result:
		docid_score = 0
		for query_term in query:
			if docid in tfidf[query_term].keys(): 
				docid_score += tfidf[query_term][docid]
		docid_score_list.append((int(docid), docid_score))
	docid_score_list = sorted(docid_score_list, key=lambda x:(-x[1], x[0]))


 # [(,)(,)(,)]
	if len(docid_score_list)<=150:
		with open("results.ranked.txt", "a") as written_file:
			for doc_score in docid_score_list: #doc_score[0]:docid  doc_score[1]: tfidf score
				print("%s,%s,%.4f" %(serial_number, doc_score[0], doc_score[1]), file=written_file)

#if the length of the list is greater than 150, we control it to only print out the first 150 elements. 
	if len(docid_score_list)>150: 
		with open("results.ranked.txt", "a") as written_file:
			for i in range(150):
				print("%s,%s,%.4f" %(serial_number, docid_score_list[i][0], docid_score_list[i][1]), file=written_file)

	


		

			