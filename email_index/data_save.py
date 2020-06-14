import os
import sqlite3
from email.parser import Parser

file_path = "emails_data"
db_path = "../email_IR/db.sqlite3"

conn = sqlite3.connect(db_path)
c = conn.cursor()


def sava_emails(file_path):
    '''save data to database'''
    email_id = 0
    sql = '''insert into email_app_email(id, messageid, date, userfrom, userto, subject, payload) 
            values (?,?,?,?,?,?,?);'''

    for root, dirs, files in os.walk(file_path):
        for file_name in files:
            email_id += 1
            print(email_id)

            f = open(os.path.join(root, file_name), 'r')
            msg = Parser().parsestr(f.read())  # parse the email
            f.close()

            para = (email_id, msg.get('Message-ID'), msg.get('Date'),
                    msg.get('From'), msg.get('To'), msg.get('Subject'), msg.get_payload())
            c.execute(sql, para)
    conn.commit()


sava_emails(file_path)
conn.close()
