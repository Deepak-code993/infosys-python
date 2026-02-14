def file_chunk(filename, chunk_size=100, output_file="chunks_output.txt"):
    with open(filename, "r") as file:
        lines = file.readlines()

    total_lines = len(lines)
    print("Total lines:", total_lines)

    chunks = [lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]
    print("Total chunks created:", len(chunks))

    with open(output_file, "w") as out:
        for index, chunk in enumerate(chunks, start=1):
            out.write(f"===== CHUNK {index} =====\n")
            out.writelines(chunk)
            out.write("\n")

    return chunks


if __name__ == "__main__":
    file_chunk("large_text.txt")
