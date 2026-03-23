"""
server.py — Flask API server for HarshScan frontend.

Endpoints:
  POST /api/analyze          — single or multi-file upload + analysis
  GET  /api/search/<job_id>  — keyword/sentiment search on job results
  GET  /api/summary/<job_id> — aggregate stats for a completed job
  GET  /api/download/<job_id>/<type> — download csv or db
  POST /api/reset            — clear a job from memory
  GET  /                     — serve index.html
"""

import os
import uuid
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename

from main import run_analysis, run_analysis_multi
from database import query_chunks, get_summary

app = Flask(__name__, static_folder=".", static_url_path="")

UPLOAD_FOLDER  = tempfile.mkdtemp(prefix="harshscan_up_")
OUTPUT_FOLDER  = tempfile.mkdtemp(prefix="harshscan_out_")
ALLOWED_EXTENSIONS = {"txt", "csv", "xlsx", "xls"}

# In-memory job store: job_id -> result dict
job_store = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Serve frontend ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# ── Analyse (single or multiple files) ──────────────────────────────────────
@app.route("/api/analyze", methods=["POST"])
def analyze():
    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No files uploaded"}), 400

    # Validate extensions
    for f in files:
        if not allowed_file(f.filename):
            return jsonify({"error": f"Unsupported file type: {f.filename}. Allowed: txt, csv, xlsx, xls"}), 400

    job_id = str(uuid.uuid4())
    job_output_dir = Path(OUTPUT_FOLDER) / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for f in files:
        if f.filename == "":
            continue
        fname = secure_filename(f.filename)
        dest  = Path(UPLOAD_FOLDER) / f"{job_id}_{fname}"
        f.save(str(dest))
        saved_paths.append(str(dest))

    if not saved_paths:
        return jsonify({"error": "No valid files to process"}), 400

    try:
        if len(saved_paths) == 1:
            result = run_analysis(saved_paths[0], output_dir=str(job_output_dir))
        else:
            result = run_analysis_multi(saved_paths, output_dir=str(job_output_dir))

        result["job_id"] = job_id
        result["files_uploaded"] = len(saved_paths)
        job_store[job_id] = result
        return jsonify(result)

    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ── Search ───────────────────────────────────────────────────────────────────
@app.route("/api/search/<job_id>")
def search(job_id):
    if job_id not in job_store:
        return jsonify({"error": "Job not found"}), 404

    job     = job_store[job_id]
    db_path = job["db_path"]
    keyword   = request.args.get("keyword", "").strip()
    sentiment = request.args.get("sentiment", "").strip()
    source    = request.args.get("source", "").strip()

    # Validate: empty keyword should return all results
    if not keyword and not sentiment and not source:
        rows = query_chunks(db_path, limit=1000)
    else:
        rows = query_chunks(db_path, keyword=keyword or None,
                            sentiment=sentiment or None,
                            source_file=source or None)

    return jsonify({"results": rows, "count": len(rows)})


# ── Summary ──────────────────────────────────────────────────────────────────
@app.route("/api/summary/<job_id>")
def summary(job_id):
    if job_id not in job_store:
        return jsonify({"error": "Job not found"}), 404
    db_path = job_store[job_id]["db_path"]
    return jsonify(get_summary(db_path))


# ── Download ─────────────────────────────────────────────────────────────────
@app.route("/api/download/<job_id>/<file_type>")
def download_file(job_id, file_type):
    if job_id not in job_store:
        return jsonify({"error": "Job not found"}), 404

    job = job_store[job_id]
    if file_type == "csv":
        path, name = job["csv_path"], "chunk_results.csv"
    elif file_type == "db":
        path, name = job["db_path"], "milestone.db"
    else:
        return jsonify({"error": "Invalid file type"}), 400

    if not Path(path).exists():
        return jsonify({"error": "File not found on server"}), 404

    return send_file(path, as_attachment=True, download_name=name)


# ── Reset ────────────────────────────────────────────────────────────────────
@app.route("/api/reset", methods=["POST"])
def reset():
    data   = request.get_json(silent=True) or {}
    job_id = data.get("job_id")
    if job_id and job_id in job_store:
        del job_store[job_id]
        return jsonify({"status": "cleared", "job_id": job_id})
    # Clear all
    job_store.clear()
    return jsonify({"status": "all cleared"})


if __name__ == "__main__":
    print("=" * 55)
    print("  HarshScan — Content Analysis Server")
    print("  http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)
