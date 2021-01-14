# coding=utf-8
import re
from preprocessing import pre_processing
from inverted_index_improved import extract_xml_file

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








