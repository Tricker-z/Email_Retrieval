import sys
import os
from nltk.tokenize import RegexpTokenizer
from email.parser import Parser

file_path = "emails_data"
chunk_path = "index_chunks"

inverted_index = dict()  # (file_id, tf)

chunk_id = file_id = 0
size_limit = 3000000
word_tokenizer = RegexpTokenizer('[A-Za-z]+')

if not os.path.exists(chunk_path):
    os.makedirs(chunk_path)


def write_chunk(inverted_index, chunk_path, chunk_id):
    output = open("{0}/chunk_{1}.txt".format(chunk_path, chunk_id), "a+")
    for term in inverted_index:
        tlst = sorted(inverted_index[term], key=lambda x: (x[0]))
        output.write("{0}:{1}\n".format(term, str(tlst)))
    output.close()


for root, dirs, files in os.walk(file_path):
    for file_name in files:
        file_id += 1
        print(file_id)

        f = open(os.path.join(root, file_name), 'r')
        msg = Parser().parsestr(f.read())  # parse the email
        f.close()

        term_count = {}  # count tf
        terms = word_tokenizer.tokenize(msg.get_payload())
        for term in terms:
            term = term.lower()
            if term not in term_count:
                term_count[term] = 0
            term_count[term] += 1

        for term in term_count:
            if term not in inverted_index:
                inverted_index[term] = list()
            inverted_index[term].append((file_id, term_count[term]))

        if sys.getsizeof(inverted_index) > size_limit:
            chunk_id += 1
            write_chunk(inverted_index, chunk_path, chunk_id)
            inverted_index.clear()

write_chunk(inverted_index, chunk_path, chunk_id)
