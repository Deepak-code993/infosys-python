def read_and_split_file(filename, chunk_size=100):
    with open(filename, "r") as file:
        lines = file.readlines()

    chunks = [
        lines[i:i + chunk_size]
        for i in range(0, len(lines), chunk_size)
    ]

    return chunks
