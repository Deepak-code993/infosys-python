from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / 'largetext.txt'

with OUTPUT_FILE.open('w', encoding='utf-8') as f:
    for i in range(1, 1001):
        f.write(f'This is line number {i}\n')

print(f'File created with 1000 lines at {OUTPUT_FILE}')
