import os
import csv

file_path = 'emails.csv' # path of downloaded csv file

r = csv.reader(open(file_path, 'r', errors='ignore'))
csv.field_size_limit(1000000000)

flag = True
file_count = 0

for row in r:
    if flag:
        flag = False
    else:
        path = "emails_data/"+row[0][:row[0].rfind("/")]
        if not os.path.exists(path):
            os.makedirs(path)

        with open("emails_data/"+row[0], "w") as f:
            f.writelines(row[1])

        file_count += 1
        print(file_count)
