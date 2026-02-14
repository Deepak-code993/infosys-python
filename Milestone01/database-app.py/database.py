import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "student.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        course TEXT
    )"""
)

conn.commit()
conn.close()
print("Database and students table are ready.")
