"""
file_handler.py — Reads TXT, CSV, and Excel files into line-chunks.
Supports single and multiple file inputs.
"""

import csv
import os


def read_txt(filename):
    """Read a plain text file and return list of lines."""
    with open(filename, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def read_csv_file(filename):
    """Read a CSV file; each row becomes one line of text."""
    lines = []
    with open(filename, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            lines.append(" ".join(str(cell) for cell in row) + "\n")
    return lines


def read_excel_file(filename):
    """Read an Excel file (.xlsx/.xls); each row becomes one line of text."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(filename, read_only=True, data_only=True)
        lines = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                row_text = " ".join(str(cell) for cell in row if cell is not None)
                if row_text.strip():
                    lines.append(row_text + "\n")
        wb.close()
        return lines
    except ImportError:
        raise ImportError("openpyxl is required for Excel support. Install it with: pip install openpyxl")


def read_file_lines(filename):
    """
    Auto-detect file type and return list of text lines.
    Supports: .txt, .csv, .xlsx, .xls
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".txt":
        return read_txt(filename)
    elif ext == ".csv":
        return read_csv_file(filename)
    elif ext in (".xlsx", ".xls"):
        return read_excel_file(filename)
    else:
        return read_txt(filename)


def read_and_split_file(filename, chunk_size=100):
    """
    Read a single file and split into chunks of chunk_size lines.
    Returns list of chunks (each chunk is a list of lines).
    """
    lines = read_file_lines(filename)
    chunks = [
        lines[i:i + chunk_size]
        for i in range(0, len(lines), chunk_size)
    ]
    return chunks


def read_and_split_multiple(filenames, chunk_size=100):
    """
    Read multiple files and return a combined list of (source_filename, chunk) tuples
    along with per-file line counts for reporting.
    """
    all_chunks = []
    file_stats = []

    for fname in filenames:
        lines = read_file_lines(fname)
        file_stats.append({
            "filename": os.path.basename(fname),
            "line_count": len(lines),
            "chunk_count": max(1, (len(lines) + chunk_size - 1) // chunk_size),
        })
        file_chunks = [
            lines[i:i + chunk_size]
            for i in range(0, len(lines), chunk_size)
        ]
        for chunk in file_chunks:
            all_chunks.append((os.path.basename(fname), chunk))

    return all_chunks, file_stats
