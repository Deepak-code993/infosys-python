def process_chunk(chunk):
    # Join lines into single text
    text = "".join(chunk)

    # Basic analysis
    word_count = len(text.split())
    error_count = text.lower().count("error")

    # Rule logic
    if error_count > 5:
        label = "High Error"
    elif error_count > 0:
        label = "Medium Error"
    else:
        label = "Clean"

    return word_count, error_count, label
