import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "student.db"
conn = sqlite3.connect(db_path)

cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            course TEXT)
""")
print("Enter student details")
name = input("Enter student name: ")
age = int(input("Enter student age: "))
course = input("Enter student course: ")

cur.execute(
    "INSERT INTO students (name, age, course) VALUES (?, ?, ?)", (name, age, course)
)
conn.commit()
conn.close()
print("done")

