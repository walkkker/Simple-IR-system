# coding=utf-8
import re
from preprocessing import pre_processing

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




