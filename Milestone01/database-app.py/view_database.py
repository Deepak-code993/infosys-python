import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'students.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(
    '''CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            course TEXT)
'''
)
cur.execute('SELECT * FROM students')
rows = cur.fetchall()
for row in rows:
    print(row)
conn.close()
