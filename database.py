import sqlite3
import csv


def setup_database():
    conn = sqlite3.connect("milestone.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunk_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_number INTEGER,
        word_count INTEGER,
        error_count INTEGER,
        trust_level TEXT,
        frequency_label TEXT,
        harsh_words_found TEXT,
        severity_score INTEGER
    )
    """)

    # Backfill schema for older databases
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(chunk_results)")]
    if "frequency_label" not in columns:
        cursor.execute("ALTER TABLE chunk_results ADD COLUMN frequency_label TEXT")
    if "harsh_words_found" not in columns:
        cursor.execute("ALTER TABLE chunk_results ADD COLUMN harsh_words_found TEXT")
    if "severity_score" not in columns:
        cursor.execute("ALTER TABLE chunk_results ADD COLUMN severity_score INTEGER")

    conn.commit()
    conn.close()


def insert_result(result):
    conn = sqlite3.connect("milestone.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chunk_results
    (chunk_number, word_count, error_count, trust_level, frequency_label, harsh_words_found, severity_score)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, result)

    conn.commit()
    conn.close()


def save_results_to_csv(results, filename="chunk_results.csv"):
    with open(filename, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["chunk_number", "word_count", "error_count", "trust_level", "frequency_label", "harsh_words_found", "severity_score"])
        writer.writerows(results)
