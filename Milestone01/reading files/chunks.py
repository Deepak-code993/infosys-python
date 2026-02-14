from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def file_chunk(filename='largetext.txt', chunk_size=100, output_file='chunks.txt'):
    input_path = BASE_DIR / filename
    output_path = BASE_DIR / output_file

    with input_path.open('r', encoding='utf-8') as file:
        lines = file.readlines()

    total_lines = len(lines)
    print('Total lines:', total_lines)

    chunks = [lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]
    print('Total chunks created:', len(chunks))

    with output_path.open('w', encoding='utf-8') as out:
        for index, chunk in enumerate(chunks, start=1):
            out.write(f'===== CHUNK {index} =====\n')
            out.writelines(chunk)
            out.write('\n')

    return chunks


if __name__ == '__main__':
    file_chunk()
