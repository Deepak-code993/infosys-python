"""
database.py — SQLite persistence and CSV export for HarshScan.
Extended schema includes sentiment columns.
"""

import sqlite3
import csv


def setup_database(db_path="milestone.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunk_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_number    INTEGER,
        source_file     TEXT,
        word_count      INTEGER,
        error_count     INTEGER,
        trust_level     TEXT,
        frequency_label TEXT,
        harsh_words_found TEXT,
        severity_score  INTEGER,
        positive_count  INTEGER DEFAULT 0,
        negative_count  INTEGER DEFAULT 0,
        neutral_count   INTEGER DEFAULT 0,
        final_sentiment TEXT DEFAULT 'Neutral',
        word_details    TEXT
    )
    """)

    # Backfill schema for older databases
    existing = [row[1] for row in cursor.execute("PRAGMA table_info(chunk_results)")]
    backfill = {
        "frequency_label":  "ALTER TABLE chunk_results ADD COLUMN frequency_label TEXT",
        "harsh_words_found":"ALTER TABLE chunk_results ADD COLUMN harsh_words_found TEXT",
        "severity_score":   "ALTER TABLE chunk_results ADD COLUMN severity_score INTEGER",
        "source_file":      "ALTER TABLE chunk_results ADD COLUMN source_file TEXT",
        "positive_count":   "ALTER TABLE chunk_results ADD COLUMN positive_count INTEGER DEFAULT 0",
        "negative_count":   "ALTER TABLE chunk_results ADD COLUMN negative_count INTEGER DEFAULT 0",
        "neutral_count":    "ALTER TABLE chunk_results ADD COLUMN neutral_count INTEGER DEFAULT 0",
        "final_sentiment":  "ALTER TABLE chunk_results ADD COLUMN final_sentiment TEXT DEFAULT 'Neutral'",
        "word_details":     "ALTER TABLE chunk_results ADD COLUMN word_details TEXT",
    }
    for col, sql in backfill.items():
        if col not in existing:
            cursor.execute(sql)

    conn.commit()
    conn.close()


def insert_result(result, db_path="milestone.db"):
    """
    result tuple:
      (index, source_file, word_count, error_count, trust, frequency_label,
       harsh_words_found, severity_score,
       positive_count, negative_count, neutral_count, final_sentiment, word_details)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO chunk_results
      (chunk_number, source_file, word_count, error_count, trust_level,
       frequency_label, harsh_words_found, severity_score,
       positive_count, negative_count, neutral_count, final_sentiment, word_details)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, result)
    conn.commit()
    conn.close()


def save_results_to_csv(results, filename="chunk_results.csv"):
    """Save all chunk results to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "chunk_number", "source_file", "word_count", "error_count",
            "trust_level", "frequency_label", "harsh_words_found", "severity_score",
            "positive_count", "negative_count", "neutral_count",
            "final_sentiment", "word_details"
        ])
        writer.writerows(results)


def query_chunks(db_path, keyword=None, sentiment=None, source_file=None, limit=500):
    """
    Search chunk_results with optional filters.
    Returns list of dicts.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    conditions = []
    params = []

    if keyword:
        kw = f"%{keyword.lower()}%"
        conditions.append(
            "(LOWER(harsh_words_found) LIKE ? OR LOWER(trust_level) LIKE ? "
            "OR LOWER(frequency_label) LIKE ? OR LOWER(final_sentiment) LIKE ? "
            "OR LOWER(source_file) LIKE ?)"
        )
        params.extend([kw, kw, kw, kw, kw])

    if sentiment:
        conditions.append("LOWER(final_sentiment) = ?")
        params.append(sentiment.lower())

    if source_file:
        conditions.append("source_file = ?")
        params.append(source_file)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"SELECT * FROM chunk_results {where} ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_summary(db_path):
    """Return aggregate statistics from chunk_results."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*)                        AS total_chunks,
            SUM(word_count)                 AS total_words,
            SUM(positive_count)             AS total_positive,
            SUM(negative_count)             AS total_negative,
            SUM(neutral_count)              AS total_neutral,
            SUM(CASE WHEN final_sentiment='Positive' THEN 1 ELSE 0 END) AS positive_chunks,
            SUM(CASE WHEN final_sentiment='Negative' THEN 1 ELSE 0 END) AS negative_chunks,
            SUM(CASE WHEN final_sentiment='Neutral'  THEN 1 ELSE 0 END) AS neutral_chunks,
            SUM(CASE WHEN harsh_words_found != 'None' THEN 1 ELSE 0 END) AS flagged_chunks,
            AVG(severity_score)             AS avg_severity
        FROM chunk_results
    """)
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "total_chunks":    row[0] or 0,
            "total_words":     row[1] or 0,
            "total_positive":  row[2] or 0,
            "total_negative":  row[3] or 0,
            "total_neutral":   row[4] or 0,
            "positive_chunks": row[5] or 0,
            "negative_chunks": row[6] or 0,
            "neutral_chunks":  row[7] or 0,
            "flagged_chunks":  row[8] or 0,
            "avg_severity":    round(row[9] or 0, 2),
        }
    return {}
