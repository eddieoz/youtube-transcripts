import sqlite3
from sqlite3 import Error

conn = None
try:
    conn = sqlite3.connect('mc_transcripts.db')
    print("db connection ok")
    conn.execute("DROP TABLE IF EXISTS transcripts")
    conn.execute("DROP TABLE IF EXISTS processed")
    conn.execute("DROP INDEX IF EXISTS index_transcripts_title")
    conn.execute('create table transcripts (title text, url text, description text)')
    conn.execute('create table processed (url text)')
    conn.execute('CREATE INDEX index_transcripts_title ON transcripts(title)')
    conn.commit()
    print ("Records created successfully")
    conn.close()
except Error as e:
    print (e)