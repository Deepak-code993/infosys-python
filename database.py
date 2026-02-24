import sqlite3

DB_NAME = "milestone.db"


def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunk_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_number INTEGER,
        word_count INTEGER,
        error_count INTEGER,
        label TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_result(chunk_number, word_count, error_count, label):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chunk_results 
    (chunk_number, word_count, error_count, label)
    VALUES (?, ?, ?, ?)
    """, (chunk_number, word_count, error_count, label))

    conn.commit()
    conn.close()
