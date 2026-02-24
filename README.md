# Harsh Words Detection and Analysis System

A Python-based text analysis tool that detects harsh, sensitive, and harmful words in document chunks, automatically classifies them by frequency, and generates comprehensive reports with severity scoring.

## 📋 Features

- **Harsh Word Detection**: Identifies 8 categories of harmful words:
  - murder, rape, suicide, homicide, genocide, assassination, abuse, molestation

- **Frequency Classification**: Automatically categorizes content based on word density:
  - **Saturated**: ≥ 10 occurrences
  - **High Frequency**: 6-9 occurrences
  - **Moderate Frequency**: 3-5 occurrences
  - **Low Frequency**: 1-2 occurrences
  - **No Usage**: 0 occurrences

- **Severity Scoring**: 1-10 scale rating based on harsh word frequency

- **Parallel Processing**: Fast chunk processing using ThreadPoolExecutor (4 workers)

- **Database Storage**: SQLite database for persistent result storage

- **CSV Export**: Detailed CSV reports for analysis and reporting

- **Comprehensive Output**: Terminal and file-based reporting with:
  - Execution time
  - Chunk number
  - Total word count
  - Detected harsh words with counts
  - Frequency labels
  - Severity scores

## 📁 Project Structure

```
project/
├── main.py                    # Main execution script
├── rule_engine.py            # Harsh word detection logic
├── file_handler.py           # Text file reading and chunking
├── database.py               # SQLite database operations
├── large_text.txt            # Sample input text file
├── chunk_results.csv         # Output results (auto-generated)
├── milestone.db              # SQLite database (auto-generated)
└── README.md                 # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.6+
- No external dependencies (uses only Python standard library)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/harsh-words-detection.git
cd harsh-words-detection
```

2. Ensure you have a text file to analyze (e.g., `large_text.txt`)

## 📖 Usage

### Basic Execution

```bash
python main.py
```

### Process Custom Text File

Edit `main.py` to change the input filename:
```python
chunks = read_and_split_file("your_file.txt")
```

### Configure Chunk Size

Modify the chunk size in `file_handler.py`:
```python
def read_and_split_file(filename, chunk_size=100):  # Change 100 to desired size
```

## 📊 Output Format

### Terminal Output
```
============================================================
HARSH WORDS DETECTION AND ANALYSIS SYSTEM
============================================================

✓ Chunk 1
  │
  ├─ Word Count          : 174
  ├─ Error Count         : 0
  ├─ Trust Level         : Trustable
  ├─ Harsh Words Found   : murder(4), abuse(5), suicide(3)
  ├─ Frequency Label     : Saturated
  └─ Severity Score (1-10): 10

==================================================
Processing Completed!
Results saved to: chunk_results.csv
Total Execution Time: 0.1234 seconds
==================================================
```

### CSV Output (chunk_results.csv)
```csv
chunk_number,word_count,error_count,trust_level,frequency_label,harsh_words_found,severity_score
1,901,0,Trustable,No usage,None,0
2,900,2,Moderately Trustable,Low frequency,"murder(1), abuse(2)",2
3,850,5,Moderately Trustable,Saturated,"murder(4), rape(2), homicide(3), genocide(2), abuse(8)",10
```

## 🔍 Output Columns Explained

| Column | Description |
|--------|-------------|
| `chunk_number` | Sequential chunk identifier (1, 2, 3, ...) |
| `word_count` | Total number of words in the chunk |
| `error_count` | Count of "error" keyword occurrences |
| `trust_level` | Trustability rating (Trustable, Moderately Trustable, Not Trustable) |
| `frequency_label` | Harsh word frequency category |
| `harsh_words_found` | List of detected words with counts (e.g., "murder(3), abuse(2)") |
| `severity_score` | Numerical severity (1-10), where 10 is most severe |

## 📈 Harsh Words List

The system detects the following words (case-insensitive):

1. **murder** - Unlawful killing
2. **rape** - Sexual assault
3. **suicide** - Self-harm
4. **homicide** - Killing of one human by another
5. **genocide** - Mass killing of ethnic/religious groups
6. **assassination** - Political killing
7. **abuse** - Mistreatment or violence
8. **molestation** - Inappropriate sexual contact

## ⚙️ Core Modules

### main.py
- Entry point for the application
- Orchestrates file reading, chunk processing, and result storage
- Displays formatted console output

### rule_engine.py
- Contains `process_chunk()` function
- Detects harsh words and counts occurrences
- Assigns frequency labels and severity scores
- Applies trust logic based on error count

### file_handler.py
- `read_and_split_file()`: Reads text file and splits into chunks
- Configurable chunk size (default: 100 lines)

### database.py
- SQLite database operations
- `setup_database()`: Creates/updates schema
- `insert_result()`: Stores results in database
- `save_results_to_csv()`: Exports results to CSV

## 💾 Database Schema

**Table: chunk_results**
```sql
CREATE TABLE chunk_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_number INTEGER,
    word_count INTEGER,
    error_count INTEGER,
    trust_level TEXT,
    frequency_label TEXT,
    harsh_words_found TEXT,
    severity_score INTEGER
)
```

## 🔧 Configuration Options

### Adjust Parallel Workers
In `main.py`, change the ThreadPoolExecutor workers:
```python
with ThreadPoolExecutor(max_workers=4) as executor:  # Change 4 to desired number
```

### Modify Trust Level Thresholds
In `rule_engine.py`, adjust error count limits:
```python
if error_count == 0:
    trust = "Trustable"
elif error_count <= 5:  # Change threshold
    trust = "Moderately Trustable"
```

### Change Frequency Thresholds
In `rule_engine.py`, adjust harsh word count limits:
```python
elif total_harsh_count >= 10:  # "Saturated" threshold
```

## 📈 Example Scenarios

### Scenario 1: Clean Text (No Harsh Words)
- Input: General news article
- Frequency Label: No usage
- Severity Score: 0
- CSV Entry: None

### Scenario 2: Light Content
- Input: Crime report with 2 harsh words
- Frequency Label: Low frequency
- Severity Score: 1-2
- CSV Entry: "murder(1), homicide(1)"

### Scenario 3: Moderate Content
- Input: Documentary with 4 harsh words
- Frequency Label: Moderate frequency
- Severity Score: 4-5

### Scenario 4: Heavy Content
- Input: Text with 15+ harsh words
- Frequency Label: Saturated
- Severity Score: 10

## 🎯 Performance

- **Processing Speed**: ~0.1 seconds for typical 5000+ word documents
- **Parallelization**: 4 concurrent workers for faster processing
- **Memory Efficient**: Processes text in chunks to minimize memory usage

## 🔐 Use Cases

- Content moderation and filtering
- Sensitive content detection
- Document classification
- Automated content warnings
- Research text analysis
- Compliance monitoring
- Safety and welfare assessments

## 📝 Notes

- All keyword matching is **case-insensitive**
- Harsh words are counted even if part of larger words (e.g., "murdered" contains "murder")
- Results are stored in both SQLite database and CSV format
- Each execution overwrites the previous CSV results
- Database entries are appended (cumulative)

## 🐛 Troubleshooting

### No results generated?
- Verify input file exists and has content
- Check file path is correct in `main.py`
- Ensure write permissions for CSV and database files

### CSV file not created?
- Check write permissions in project directory
- Verify database was created successfully

### Slow processing?
- Reduce chunk size for faster processing
- Increase ThreadPoolExecutor workers

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Add more harmful word categories
- Implement word-boundary detection (to avoid partial matches)
- Add GUI interface
- Support for multiple languages
- Machine learning-based classification

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created for content analysis and moderation purposes.

## 📞 Support

For issues or questions, please create an issue in the repository.

---

**Last Updated**: February 2026
**Version**: 1.0.0
