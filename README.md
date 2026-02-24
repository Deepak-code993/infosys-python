# Parallel Text Chunk Analyzer (Python + SQLite)

This project processes a large text file in chunks, analyzes each chunk using a simple rule engine, and stores the results in a SQLite database.

It is built as a modular Python application to demonstrate:
- File handling and chunking
- Parallel processing with threads
- Rule-based text classification
- SQLite integration for persistent results

## Features

- Reads `large_text.txt` and splits it into fixed-size chunks (default: 100 lines per chunk)
- Processes chunks in parallel using `ThreadPoolExecutor`
- Calculates per-chunk:
  - Word count
  - Error count (occurrences of the word `error`, case-insensitive)
  - Trust level
- Stores results into `milestone.db` (`chunk_results` table)
- Automatically handles older DB schema by adding `trust_level` column if missing

## Project Structure

```text
project/
├── main.py            # Entry point: orchestration + parallel execution
├── file_handler.py    # File read + chunk split logic
├── rule_engine.py     # Chunk analysis + trust classification
├── database.py        # SQLite setup + insert operations
├── large_text.txt     # Input text file to process
├── milestone.db       # SQLite database (created/updated at runtime)
└── README.md
```

## Requirements

- Python 3.8+
- No external packages required (uses only Python standard library)

## How It Works

1. `main.py` reads `large_text.txt` through `read_and_split_file(...)`.
2. The file is split into chunks (`chunk_size=100` lines by default).
3. Each chunk is processed in parallel (`max_workers=4`) via `process_chunk(...)`.
4. For each chunk, the program computes:
   - `word_count`: total words
   - `error_count`: number of times `error` appears
   - `trust_level`:
     - `Trustable` if `error_count == 0`
     - `Moderately Trustable` if `error_count <= 5`
     - `Not Trustable` otherwise
5. Results are inserted into SQLite table `chunk_results`.

## Setup and Run

From the project root:

```bash
python main.py
```

On some systems, use:

```bash
python3 main.py
```

## Example Console Output

```text
Reading file and creating chunks...
Total chunks created: 12
Processing chunks in parallel...

Chunk 1
  Word Count   : 1450
  Error Count  : 2
  Trust Level  : Moderately Trustable
----------------------------------------
...
Processing Completed!
Total Execution Time: 0.1234 seconds
```

## Database Details

Database file: `milestone.db`

Table: `chunk_results`

| Column        | Type    | Description                       |
|---------------|---------|-----------------------------------|
| id            | INTEGER | Auto-increment primary key        |
| chunk_number  | INTEGER | Chunk index (starting at 1)       |
| word_count    | INTEGER | Number of words in the chunk      |
| error_count   | INTEGER | Count of `error` occurrences      |
| trust_level   | TEXT    | Trust classification label        |

## Customization

- Change chunk size:
  - Edit `read_and_split_file("large_text.txt")` in `main.py`
  - Or pass `chunk_size` explicitly (e.g., `chunk_size=50`)
- Change parallelism:
  - Update `ThreadPoolExecutor(max_workers=4)` in `main.py`
- Change trust rules:
  - Modify logic in `rule_engine.py`

## Notes and Limitations

- Running the script multiple times appends new rows to `chunk_results`.
- The current parser treats `error` as a substring match in lowercased text.
- Input file path is currently hardcoded as `large_text.txt`.

## Suggested Next Improvements

- Add command-line arguments for input file, chunk size, and worker count
- Add unit tests for chunking, rule logic, and DB writes
- Add a query/report script for summarizing stored results
- Add CSV/JSON export option

## License

Choose and add a license file before publishing publicly on GitHub (for example, MIT).

