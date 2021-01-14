import collections
import re
import math
from stemming.porter2 import stem

def tokenization(content):
	#delete "'" from the punctuation set, because in the stop words file, some stop words invlove "'".
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

# set() delete the replicated word
def positional_inverted_index():
	file_tokens_all =[]
	file_tokens=[]
	file_info=[]
	xml_content = extract_xml_file("trec.5000.xml")
	for single_file in xml_content:
		# headline + text   format of file_info: [(docid, [tokens of headline + text]),(),(),(),()]
		file_tokens_all += pre_processing(single_file[1]) + pre_processing(single_file[2])
		file_tokens= pre_processing(single_file[1]) + pre_processing(single_file[2])
		file_info.append((single_file[0], file_tokens))

	inverted_index = dict()

	set_tokens = set(file_tokens_all)
		
	for term in set_tokens:
		list_of_term_inverted_index=[]
		for single_file in file_info:
#single_file[0]: docID      single_file[1]: headline   single_file[2]: content
#single_file[0]:doc_id   single_file[1]: single_file_tokens
			if term in single_file[1]:
				list_of_positions = []
				for i in range(1, len(single_file[1])+1):
					if term == single_file[1][i-1]:
						list_of_positions.append(i)
				list_of_term_inverted_index.append((single_file[0], list_of_positions))

	#the list of tuples [(), (), ()]
		inverted_index[term]=list_of_term_inverted_index



	#Reference: doc_info[0] = docID  ;   doc_info[1] = list of positions
	with open("index.txt", "w") as written_file:
		for key_of_term in sorted(inverted_index):
			print("%s:%i" %(key_of_term, len(inverted_index[key_of_term])), file = written_file)
			for doc_info in inverted_index[key_of_term]:
				print("\t%s:" %doc_info[0], ",".join(str(i) for i in doc_info[1]), file=written_file)  #why is %s
			print(file=written_file)
	return inverted_index


def extract_xml_file(file_path):
	with open(file_path, 'r') as f:
		#for collection.xml not real assignment ::: xml_content = re.findall(r"<DOCNO>(\d+?)</DOCNO>.*?<Text>.*?(\w.*?)\n\s*?</Text>", f.read(), re.DOTALL)
		# xml_content: list ******** for single_file in xml_content: single_file[0] is docID, single_file[1] is the headline, single_file[2] is the content
		xml_content = re.findall(r"<DOCNO>(\d+)</DOCNO>.*?<HEADLINE>\n(.+?)\n</HEADLINE>.*?<TEXT>\n(.*?)</TEXT>", f.read(), re.DOTALL)
		return xml_content

def phrase_search(query, inverted_index):
	phrase_search_result_list = []
	query_info = re.findall(r'(\w+)\s"(\w+)\s(\w+)"', query, re.DOTALL)
	#phrase_list[0] phrase_list[1]
	#pre_processing returns a list involving only one element. so pre_processing('str')[0]=='str'
	serial_number = query_info[0][0]
	first_term = pre_processing(query_info[0][1])[0]
	second_term = pre_processing(query_info[0][2])[0]
	if first_term in inverted_index.keys() and second_term in inverted_index.keys():
		for doc_info_of_first_term in inverted_index[first_term]: #doc_info[0] docID; doc_info[1] list of positions
			for doc_info_of_second_term in inverted_index[second_term]:
				if doc_info_of_first_term[0] == doc_info_of_second_term[0]:
					for position_of_second_term in doc_info_of_second_term[1]:
						for position_of_first_term in doc_info_of_first_term[1]:
							if (position_of_second_term - position_of_first_term) == 1:
								phrase_search_result_list.append(doc_info_of_first_term[0])
								break
						else:
							continue
						break
					break
	list_of_docid = [int(docid) for docid in phrase_search_result_list]
	with open("results.boolean.txt", "a") as written_file:
		for docid in sorted(list_of_docid): 
			print("%s,%s" %(serial_number, docid), file=written_file)



def proximity_search(query, inverted_index):
	query_info = re.findall(r"(\w+)\s#(\d+)\((\w+),\s?(\w+)\)", query, re.DOTALL)
	list_of_docid = []
	#phrase_list[0] phrase_list[1]
	#query_info is a list which involve a 3-D tuple    [(proximity_num, first_term, second_term)]
	serial_number = query_info[0][0]
	proximity_num = int(query_info[0][1]) # str->int
	first_term = pre_processing(query_info[0][2])[0]
	second_term = pre_processing(query_info[0][3])[0]
	if first_term in inverted_index.keys() and second_term in inverted_index.keys():
		for doc_info_of_first_term in inverted_index[first_term]: #doc_info[0] docID; doc_info[1] list of positions
			for doc_info_of_second_term in inverted_index[second_term]:
				if doc_info_of_first_term[0] == doc_info_of_second_term[0]:
					for position_of_second_term in doc_info_of_second_term[1]:
						for position_of_first_term in doc_info_of_first_term[1]:
							if abs(position_of_second_term - position_of_first_term) <= proximity_num:
								list_of_docid.append(doc_info_of_first_term[0])
								#with open("results.boolean.txt", "a") as written_file:
									#print("%s, %s" %(serial_number, doc_info_of_first_term[0]), file=written_file)
								break
						else:
							continue
						break
					break

	list_of_docid = [int(docid) for docid in list_of_docid]
	if len(list_of_docid) != 0:
		with open("results.boolean.txt", "a") as written_file:
			for docid in sorted(list_of_docid): 
				print("%s,%s" %(serial_number, docid), file=written_file)
	

def phrase_boolean_term(query, inverted_index):
	phrase_search_result_list = []
	term_search_result_list = []

	query_info = re.findall(r'(\w+)\s"(\w+)\s(\w+)"\s(.+)\s(\w+)', query, re.DOTALL)
	serial_number = query_info[0][0]
	first_term_of_phrase = pre_processing(query_info[0][1])[0]
	second_term_of_phrase = pre_processing(query_info[0][2])[0]
	operator = query_info[0][3]
	second_term = pre_processing(query_info[0][4])[0]
#query result for phrase
#ATTENTION: NEED TO EDIT AGAIN usage: calculate the phrase search result list
	phrase_search_result_list = []
	if first_term_of_phrase in inverted_index.keys() and second_term_of_phrase in inverted_index.keys():
		for doc_info_of_first_term in inverted_index[first_term_of_phrase]: #doc_info[0] docID; doc_info[1] list of positions
			for doc_info_of_second_term in inverted_index[second_term_of_phrase]:
				if doc_info_of_first_term[0] == doc_info_of_second_term[0]:
					for position_of_second_term in doc_info_of_second_term[1]:
						for position_of_first_term in doc_info_of_first_term[1]:
							if (position_of_second_term - position_of_first_term) == 1:
								with open("results.boolean.txt", "a") as written_file:
									#print("%s, %s" %(serial_number, doc_info_of_first_term[0]), file=written_file)
									phrase_search_result_list.append(doc_info_of_first_term[0])
								break
						else:
							continue
						break
					break
	
	if len(phrase_search_result_list) != 0 and second_term in inverted_index.keys():
#query result for single term
		for doc_info_of_second_term in inverted_index[second_term]:
			term_search_result_list.append(doc_info_of_second_term[0])

		if operator == 'AND':
			list_of_docid = [docid for docid in phrase_search_result_list if docid in term_search_result_list]
		if operator == 'OR':
			list_of_docid = list(set(phrase_search_result_list + term_search_result_list)) #set() delete the same element and sort all elements in the list
		if operator == 'AND NOT':
			list_of_docid = [docid for docid in phrase_search_result_list if docid not in term_search_result_list]
		if operator == 'OR NOT':
			all_docid = []
			xml_content = extract_xml_file("trec.5000.xml") # single_file[0]: docid;   single_file[1]: headline+text
			for single_file in xml_content:
				all_docid.append(single_file[0])
			not_term_docid = [x for x in all_docid if x not in term_search_result_list]
			list_of_docid = list(set(phrase_search_result_list + not_term_docid))


		list_of_docid = [int(docid) for docid in list_of_docid]
		if len(list_of_docid) != 0:
			with open("results.boolean.txt", "a") as written_file:
				for docid in sorted(list_of_docid): 
					print("%s,%s" %(serial_number, docid), file=written_file)



def term_boolean_term(query, inverted_index):
	
	query_info = re.findall(r"(\w+)\s(\w+)\s(.+)\s(\w+)", query, re.DOTALL)
	serial_number = query_info[0][0]
	first_term = pre_processing(query_info[0][1])[0]
	operator = query_info[0][2]
	second_term = pre_processing(query_info[0][3])[0]
	if first_term in inverted_index.keys() and second_term in inverted_index.keys():
		list_of_first_term = []
		list_of_second_term = []
		for doc_info_of_first_term in inverted_index[first_term]:    #doc_info_of_X_term [0] docID; doc_info_of_X_term[1] list of positions
			list_of_first_term.append(doc_info_of_first_term[0])
		for doc_info_of_second_term in inverted_index[second_term]:
			list_of_second_term.append(doc_info_of_second_term[0])

		if operator == "AND":
			list_of_docid = [docid for docid in list_of_first_term if docid in list_of_second_term]
							
		if operator == "OR":
			list_of_docid = list(set(list_of_first_term+list_of_second_term))
									
		if operator == "AND NOT":
			list_of_docid = [docid for docid in list_of_first_term if docid not in list_of_second_term]
		#print the search result

		if operator == 'OR NOT':
			all_docid = []
			xml_content = extract_xml_file("trec.5000.xml") # single_file[0]: docid;   single_file[1]: headline+text
			for single_file in xml_content:
				all_docid.append(single_file[0])
			not_second_term_docid = [x for x in all_docid if x not in list_of_second_term]
			list_of_docid = list(set(list_of_first_term + not_second_term_docid))

		list_of_docid = [int(docid) for docid in list_of_docid]
		if len(list_of_docid) != 0:
			with open("results.boolean.txt", "a") as written_file:
				for docid in sorted(list_of_docid): 
					print("%s,%s" %(serial_number, docid), file=written_file)


def single_term_search(query, inverted_index):
	query_info = re.findall(r"(\w+)\s(\w+)", query, re.DOTALL)
	serial_number = query_info[0][0]
	search_term = pre_processing(query_info[0][1])[0]
	search_term_list = []
	if search_term in inverted_index.keys():
		for doc_info_of_search_term in inverted_index[search_term]:
			search_term_list.append(doc_info_of_search_term[0])

	#if len(search_term_list) != 0:
	with open("results.boolean.txt", "a") as written_file:
		for docid in search_term_list: 
			print("%s,%s" %(serial_number, docid), file=written_file)



def phrase_boolean_phrase(query, inverted_index):

	query_info = re.findall(r'(\w+)\s"(\w+)\s(\w+)"\s(.+)\s"(\w+)\s(\w+)"', query, re.DOTALL)
	serial_number = query_info[0][0]
	first_term_of_first_phrase = pre_processing(query_info[0][1])[0]
	second_term_of_first_phrase = pre_processing(query_info[0][2])[0]
	operator = query_info[0][3]
	first_term_of_second_phrase = pre_processing(query_info[0][4])[0]
	second_term_of_second_phrase = pre_processing(query_info[0][5])[0]
#query result for phrase
#ATTENTION: NEED TO EDIT AGAIN usage: calculate the phrase search result list
	first_phrase_list = []
	if first_term_of_first_phrase in inverted_index.keys() and second_term_of_first_phrase in inverted_index.keys():
		for doc_info_of_first_term in inverted_index[first_term_of_first_phrase]: #doc_info[0] docID; doc_info[1] list of positions
			for doc_info_of_second_term in inverted_index[second_term_of_first_phrase]:
				if doc_info_of_first_term[0] == doc_info_of_second_term[0]:
					for position_of_second_term in doc_info_of_second_term[1]:
						for position_of_first_term in doc_info_of_first_term[1]:
							if (position_of_second_term - position_of_first_term) == 1:								
								first_phrase_list.append(doc_info_of_first_term[0])
								break
						else:
							continue
						break
					break

	second_phrase_list = []
	if first_term_of_second_phrase in inverted_index.keys() and second_term_of_second_phrase in inverted_index.keys():
		for doc_info_of_first_term in inverted_index[first_term_of_second_phrase]: #doc_info[0] docID; doc_info[1] list of positions
			for doc_info_of_second_term in inverted_index[second_term_of_second_phrase]:
				if doc_info_of_first_term[0] == doc_info_of_second_term[0]:
					for position_of_second_term in doc_info_of_second_term[1]:
						for position_of_first_term in doc_info_of_first_term[1]:
							if (position_of_second_term - position_of_first_term) == 1:
								second_phrase_list.append(doc_info_of_first_term[0])
								break
						else:
							continue
						break
					break
	
	
	if len(first_phrase_list) != 0 and len(second_phrase_list) != 0:
		if operator == 'AND':
			list_of_docid = [docid for docid in first_phrase_list if docid in second_phrase_list]
		if operator == 'OR':
			list_of_docid = list(set(first_phrase_list + second_phrase_list)) #set() delete the same element and sort all elements in the list
		if operator == 'AND NOT':
			list_of_docid = [docid for docid in first_phrase_list if docid not in second_phrase_list]
		if operator == 'OR NOT':
			all_docid = []
			xml_content = extract_xml_file("trec.5000.xml") # single_file[0]: docid;   single_file[1]: headline+text
			for single_file in xml_content:
				all_docid.append(single_file[0])
			not_term_docid = [x for x in all_docid if x not in second_phrase_list]
			list_of_docid = list(set(first_phrase_list + not_term_docid))


		list_of_docid = [int(docid) for docid in list_of_docid]
		if len(list_of_docid) != 0:
			with open("results.boolean.txt", "a") as written_file:
				for docid in sorted(list_of_docid): 
					print("%s,%s" %(serial_number, docid), file=written_file)


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
