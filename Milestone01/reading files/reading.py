# generate_file.py
with open("large_text.txt", "w") as f:
    for i in range(1, 1001):
        f.write(f"This is line number {i}\n")

print("File created with 1000 lines")
