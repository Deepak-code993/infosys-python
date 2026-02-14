import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "student.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT * FROM students")
rows = cur.fetchall()
for row in rows:
    print(row)
conn.close()
