# HarshScan — Content Analysis Dashboard (Python + Flask)

HarshScan is a small Python project that analyzes text datasets in **chunks** and produces per‑chunk metrics:
harsh/violent keyword usage, basic “trust” labeling (based on the word `error`), and a simple lexicon-based sentiment score.

It can be used in two ways:
- **Web UI**: run a Flask server (`server.py`) and use the dashboard in `index.html`
- **CLI**: run `main.py` to analyze a local text file and write results to CSV + SQLite

---

## Features

- Upload and analyze **.txt**, **.csv**, **.xlsx/.xls** files (single or multiple) via a browser UI
- Chunking (default: **100 lines per chunk**) for large files
- Parallel processing using `ThreadPoolExecutor`
- Per-chunk output:
  - word count
  - `error` count → trust label (`Trustable` / `Moderately Trustable` / `Not Trustable`)
  - harsh word frequency label + severity score (0–10)
  - sentiment counts (positive/negative/neutral) + final sentiment label
- Results export:
  - `chunk_results.csv`
  - `milestone.db` (SQLite)

---

## Quickstart (Web UI)

1) Install dependencies:

```bash
pip install flask openpyxl
```

Notes:
- `openpyxl` is only required for Excel uploads (`.xlsx/.xls`).
- The UI loads fonts (Google Fonts) and Chart.js from CDNs; an internet connection improves the UI, but the backend works offline.

2) Start the server:

```bash
python server.py
```

3) Open the dashboard:

- `http://localhost:5000`

---

## Quickstart (CLI)

`main.py` looks for an input file in the current directory named **either**:
- `large_text.txt`
- `test_harsh_words.txt`

Then run:

```bash
python main.py
```

Outputs are written to the current folder:
- `chunk_results.csv`
- `milestone.db`

---

## API Endpoints (Flask)

The server provides:
- `GET /` — serves `index.html`
- `POST /api/analyze` — upload one or more files under the `files` form field
- `GET /api/search/<job_id>?keyword=&sentiment=&source=` — query stored chunk results
- `GET /api/summary/<job_id>` — aggregate stats for a job
- `GET /api/download/<job_id>/<type>` — download job output (`type` is `csv` or `db`)
- `POST /api/reset` — clear one job (pass JSON `{"job_id":"..."}`) or all jobs (empty JSON)

Example `curl` upload:

```bash
curl -F "files=@large_text.txt" http://localhost:5000/api/analyze
```

---

## How The Analysis Works (High Level)

- **Chunking**: files are read into lines and split into chunks of 100 lines (`file_handler.py`).
- **Parallel processing**: chunks are processed with `ThreadPoolExecutor` (`main.py`).
- **Harsh words**: a fixed list in `rule_engine.py` is counted with substring matches.
- **Trust label**: based on how many times the word `error` appears in the chunk.
- **Sentiment**: lexicon-based scoring with simple negation/amplifier handling (`rule_engine.py`).
- **Persistence**: each chunk row is stored in SQLite and exported to CSV (`database.py`).

---

## Project Structure

- `server.py` — Flask API + serves `index.html`
- `index.html` — single-file dashboard (HTML/CSS/JS) that calls the API
- `main.py` — orchestration layer; runs analysis and writes CSV/SQLite
- `rule_engine.py` — harsh word detection + sentiment scoring + `process_chunk`
- `file_handler.py` — reads `.txt` / `.csv` / `.xlsx/.xls` and splits into chunks
- `database.py` — SQLite schema, inserts, CSV export, search + summary helpers

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'`**
  - Run `pip install flask`
- **`ImportError: openpyxl is required for Excel support...`**
  - Run `pip install openpyxl` (only needed for `.xlsx/.xls`)
- **CLI raises `FileNotFoundError: No input file found...`**
  - Create `large_text.txt` (or `test_harsh_words.txt`) in the same folder as `main.py`, then rerun.

---

## Notes / Limitations

- Harsh-word detection uses simple substring counts; it is not NLP/ML-based.
- The frontend references “MIT License” text in the UI, but this repository does not include a `LICENSE` file.

