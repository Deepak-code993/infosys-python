import time
from concurrent.futures import ThreadPoolExecutor
from database import insert_result, save_results_to_csv, setup_database
from file_handler import read_and_split_file
from rule_engine import process_chunk


def main():
    start_time = time.time()

    print("\n" + "=" * 60)
    print("HARSH WORDS DETECTION AND ANALYSIS SYSTEM")
    print("=" * 60)
    print("\nReading file and creating chunks...\n")
    chunks = read_and_split_file("test_harsh_words.txt")

    print(f"Total chunks created: {len(chunks)}\n")

    setup_database()

    print("Processing chunks in parallel...\n")
    print("=" * 60)

    csv_results = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(
            process_chunk,
            [(index, chunk) for index, chunk in enumerate(chunks, start=1)]
        )

        for result in results:
            index, word_count, error_count, trust, frequency_label, harsh_words_found, severity_score = result

            print(f"\n✓ Chunk {index}")
            print(f"  │")
            print(f"  ├─ Word Count          : {word_count}")
            print(f"  ├─ Error Count         : {error_count}")
            print(f"  ├─ Trust Level         : {trust}")
            print(f"  ├─ Harsh Words Found   : {harsh_words_found}")
            print(f"  ├─ Frequency Label     : {frequency_label}")
            print(f"  └─ Severity Score (1-10): {severity_score}")

            insert_result(result)
            csv_results.append(result)

    save_results_to_csv(csv_results, "harsh_words_analysis.csv")

    end_time = time.time()
    execution_time = end_time - start_time

    print("\n" + "=" * 60)
    print("Processing Completed!")
    print("Results saved to: harsh_words_analysis.csv")
    print(f"Total Execution Time: {execution_time:.4f} seconds")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
