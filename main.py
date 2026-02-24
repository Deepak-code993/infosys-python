from pathlib import Path

from file_handler import read_and_split_file
from rule_engine import process_chunk
from database import setup_database, insert_result

PROJECT_ROOT = Path(__file__).resolve().parent



def main():
    print("Reading file and splitting into chunks...")
    chunks = read_and_split_file(str(PROJECT_ROOT / "large_text.txt"))

    print("Setting up database...")
    setup_database()

    print("Processing chunks...")

    for index, chunk in enumerate(chunks, start=1):
        word_count, error_count, label = process_chunk(chunk)

        insert_result(index, word_count, error_count, label)

        print(f"Chunk {index} processed and stored.")

    print("All chunks processed successfully!")


if __name__ == "__main__":
    main()
