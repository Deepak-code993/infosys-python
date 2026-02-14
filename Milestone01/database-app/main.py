import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'students.db'
conn = sqlite3.connect(DB_PATH)

cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            course TEXT)
''')

print('Enter student details')
name = input('Enter student name: ')
age = int(input('Enter student age: '))
course = input('Enter student course: ')

cur.execute(
    'INSERT INTO students (name, age, course) VALUES (?, ?, ?)', (name, age, course)
)
conn.commit()
conn.close()
print('done')
