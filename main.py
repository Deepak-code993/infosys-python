"""
main.py — Orchestration layer for HarshScan.

Key functions:
  run_analysis(input_file, output_dir)  — single file, parallel processing
  run_analysis_multi(files, output_dir) — multiple files, parallel + serial timing comparison
"""

import time
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from database import insert_result, save_results_to_csv, setup_database
from file_handler import read_and_split_file, read_and_split_multiple
from rule_engine import process_chunk

NUM_WORKERS = max(2, os.cpu_count() or 4)


def _run_serial(indexed_chunks):
    """Process chunks one-by-one (for timing comparison)."""
    return [process_chunk(item) for item in indexed_chunks]


def _run_parallel(indexed_chunks, workers=NUM_WORKERS):
    """Process chunks using ThreadPoolExecutor."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(process_chunk, indexed_chunks))


def run_analysis(input_file, output_dir="."):
    """
    Single-file analysis with parallel vs serial timing comparison.
    Returns rich result dict for API consumption.
    """
    start_total = time.time()

    db_path  = str(Path(output_dir) / "milestone.db")
    csv_path = str(Path(output_dir) / "chunk_results.csv")

    setup_database(db_path)

    chunks = read_and_split_file(input_file)
    file_stats = [{
        "filename":    Path(input_file).name,
        "line_count":  sum(len(c) for c in chunks),
        "chunk_count": len(chunks),
    }]

    # Build indexed items: (index, source_file, chunk)
    indexed = [
        (i + 1, Path(input_file).name, chunk)
        for i, chunk in enumerate(chunks)
    ]

    # ── Serial timing (on up to 500 chunks to keep it fast) ──────────────────
    sample = indexed[:min(len(indexed), 500)]
    t0 = time.perf_counter()
    _run_serial(sample)
    serial_time = round(time.perf_counter() - t0, 4)

    # ── Parallel processing (full dataset) ───────────────────────────────────
    t0 = time.perf_counter()
    results = _run_parallel(indexed, workers=NUM_WORKERS)
    parallel_time = round(time.perf_counter() - t0, 4)

    # ── Persist ──────────────────────────────────────────────────────────────
    csv_rows = []
    chunk_outputs = []

    for result in results:
        (idx, src, wc, ec, trust, freq, harsh, sev,
         pos, neg, neu, sentiment, wdetail) = result

        insert_result(result, db_path)
        csv_rows.append(result)

        chunk_outputs.append({
            "chunk":            idx,
            "source_file":      src,
            "word_count":       wc,
            "error_count":      ec,
            "trust_level":      trust,
            "frequency_label":  freq,
            "harsh_words_found": harsh,
            "severity_score":   sev,
            "positive_count":   pos,
            "negative_count":   neg,
            "neutral_count":    neu,
            "final_sentiment":  sentiment,
        })

    save_results_to_csv(csv_rows, csv_path)

    total_time = round(time.time() - start_total, 4)

    return {
        "input_file":     str(input_file),
        "total_chunks":   len(chunks),
        "file_stats":     file_stats,
        "execution_time": total_time,
        "serial_time":    serial_time,
        "parallel_time":  parallel_time,
        "num_workers":    NUM_WORKERS,
        "chunks":         chunk_outputs,
        "csv_path":       csv_path,
        "db_path":        db_path,
    }


def run_analysis_multi(input_files, output_dir="."):
    """
    Multi-file analysis with parallel vs serial timing comparison.
    All files are combined into one job; results saved to shared DB + CSV.
    """
    start_total = time.time()

    db_path  = str(Path(output_dir) / "milestone.db")
    csv_path = str(Path(output_dir) / "chunk_results.csv")

    setup_database(db_path)

    all_named_chunks, file_stats = read_and_split_multiple(input_files)

    # Build indexed items: (global_index, source_file, chunk)
    indexed = [
        (i + 1, named[0], named[1])
        for i, named in enumerate(all_named_chunks)
    ]

    # ── Serial timing ─────────────────────────────────────────────────────────
    sample = indexed[:min(len(indexed), 500)]
    t0 = time.perf_counter()
    _run_serial(sample)
    serial_time = round(time.perf_counter() - t0, 4)

    # ── Parallel processing ───────────────────────────────────────────────────
    t0 = time.perf_counter()
    results = _run_parallel(indexed, workers=NUM_WORKERS)
    parallel_time = round(time.perf_counter() - t0, 4)

    # ── Persist ──────────────────────────────────────────────────────────────
    csv_rows = []
    chunk_outputs = []

    for result in results:
        (idx, src, wc, ec, trust, freq, harsh, sev,
         pos, neg, neu, sentiment, wdetail) = result

        insert_result(result, db_path)
        csv_rows.append(result)

        chunk_outputs.append({
            "chunk":            idx,
            "source_file":      src,
            "word_count":       wc,
            "error_count":      ec,
            "trust_level":      trust,
            "frequency_label":  freq,
            "harsh_words_found": harsh,
            "severity_score":   sev,
            "positive_count":   pos,
            "negative_count":   neg,
            "neutral_count":    neu,
            "final_sentiment":  sentiment,
        })

    save_results_to_csv(csv_rows, csv_path)

    total_time = round(time.time() - start_total, 4)

    return {
        "input_files":    [str(f) for f in input_files],
        "total_chunks":   len(indexed),
        "file_stats":     file_stats,
        "execution_time": total_time,
        "serial_time":    serial_time,
        "parallel_time":  parallel_time,
        "num_workers":    NUM_WORKERS,
        "chunks":         chunk_outputs,
        "csv_path":       csv_path,
        "db_path":        db_path,
    }


def main():
    """CLI entry point — processes large_text.txt or test_harsh_words.txt."""
    from pathlib import Path
    input_candidates = ["large_text.txt", "test_harsh_words.txt"]
    input_file = next((n for n in input_candidates if Path(n).exists()), None)

    if input_file is None:
        raise FileNotFoundError(
            "No input file found. Expected one of: large_text.txt, test_harsh_words.txt"
        )

    result = run_analysis(input_file)

    print(f"\n{'='*55}")
    print(f"  HarshScan — Results")
    print(f"{'='*55}")
    print(f"  File         : {result['input_file']}")
    print(f"  Chunks       : {result['total_chunks']}")
    print(f"  Serial time  : {result['serial_time']}s (sample)")
    print(f"  Parallel time: {result['parallel_time']}s (full, {result['num_workers']} workers)")
    print(f"  Total time   : {result['execution_time']}s")
    print(f"{'='*55}\n")

    for c in result["chunks"]:
        print(f"Chunk {c['chunk']} [{c['source_file']}]")
        print(f"  Words: {c['word_count']}  |  Errors: {c['error_count']}  |  Trust: {c['trust_level']}")
        print(f"  Sentiment: {c['final_sentiment']}  (pos={c['positive_count']}, neg={c['negative_count']}, neu={c['neutral_count']})")
        print(f"  Harsh: {c['harsh_words_found']}  |  Severity: {c['severity_score']}/10")
        print("-" * 55)

    print(f"\nResults saved to: {result['csv_path']}")


if __name__ == "__main__":
    main()
