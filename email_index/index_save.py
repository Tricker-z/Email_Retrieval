import os
from math import log
import sqlite3

chunk_path = "index_chunks"
db_path = "../email_IR/db.sqlite3"

inverted_index = dict()
doc_len = dict()

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

    doc_num = 517401
    for term in inverted_index:
        inverted_index[term][1] = sorted(
            inverted_index[term][1], key=lambda x: (x[0]))
        inverted_index[term][0] = doc_num/len(inverted_index[term][1])  # N/df

    # calculate document vector length
    for term in inverted_index:
        idf = log(inverted_index[term][0], 10)
        for doc, tf in inverted_index[term][1]:
            wf = 1+log(tf, 10)
            if doc not in doc_len:
                doc_len[doc] = 0
            doc_len[doc] += pow(wf*idf, 2)


# save index and doc_len to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

term_count = 0
sql_index = "insert into email_app_index(term, ndf, posting) VALUES (?,?,?);"
for term in inverted_index:
    term_count += 1
    print("term", term_count)
    para = (term, inverted_index[term][0], str(inverted_index[term][1]))
    c.execute(sql_index, para)
conn.commit()

doc_count = 0
sql_len = "insert into email_app_filelength(id, length) values (?,?);"
for doc in doc_len:
    doc_count += 1
    print("doc", doc_count)
    para = (doc, doc_len[doc]**0.5)
    c.execute(sql_len, para)
conn.commit()

conn.close()
