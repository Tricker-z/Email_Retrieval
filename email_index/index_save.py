import os
from math import log
import sqlite3

chunk_path = "index_chunks"
db_path = "../email_IR/db.sqlite3"
doc_num = 517401

inverted_index = dict()
doc_len = [0 for i in range(doc_num)]

file_count = 0
for root, dirs, files in os.walk(chunk_path, True):
    # merge the chunks
    for filename in files:
        file_count += 1
        print('Merge chunk', file_count)

        f = open(os.path.join(root, filename), 'r')
        for line in f.readlines():
            term = line.split(":")[0]
            doc_list = eval(line.split(":")[1])
            if term not in inverted_index:
                inverted_index[term] = [0, list()]
            inverted_index[term][1] = inverted_index[term][1] + doc_list
        f.close()

    for term in inverted_index:
        inverted_index[term][1] = sorted(
            inverted_index[term][1], key=lambda x: (x[0]))
        inverted_index[term][0] = doc_num/len(inverted_index[term][1])  # N/df

    # calculate document vector length
    for term in inverted_index:
        idf = log(inverted_index[term][0], 10)
        for doc, tf in inverted_index[term][1]:
            wf = 1+log(tf, 10)
            doc_len[doc-1] += pow(wf*idf, 2)
    for i in range(doc_num):
        doc_len[i] = doc_len[i]**0.5


# save index to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

term_count = 0
sql_index = '''insert into email_app_index(term, ndf, posting) VALUES (?,?,?);'''
for term in inverted_index:
    term_count += 1
    print("Term", term_count)
    para = (term, inverted_index[term][0], str(inverted_index[term][1]))
    c.execute(sql_index, para)
conn.commit()
conn.close()

# write document length to file
output = open('static/doc_length.txt', 'a+')
output.write(str(doc_len))
output.close()

# generate 3-gram index
three_gram_index = dict()

for term in inverted_index:
    for i in range(len(term)-2):
        gram = term[i:i+3]
        if gram not in three_gram_index:
            three_gram_index[gram] = []
        three_gram_index[gram].append(term)

gram_write = open('static/three_gram_index.txt', 'a+')
gram_write.write(str(three_gram_index))
gram_write.close()
