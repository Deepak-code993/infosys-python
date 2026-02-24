def process_chunk(data):
    index, chunk = data

    # Harsh words to detect
    HARSH_WORDS = ['murder', 'rape', 'suicide', 'homicide', 'genocide', 'assassination', 'abuse', 'molestation']
    
    text = "".join(chunk)
    word_count = len(text.split())
    error_count = text.lower().count("error")

    # Trust Logic
    if error_count == 0:
        trust = "Trustable"
    elif error_count <= 5:
        trust = "Moderately Trustable"
    else:
        trust = "Not Trustable"

    # Detect harsh words and count occurrences
    lower_text = text.lower()
    harsh_word_counts = {}
    total_harsh_count = 0
    
    for word in HARSH_WORDS:
        count = lower_text.count(word)
        if count > 0:
            harsh_word_counts[word] = count
            total_harsh_count += count
    
    # Determine frequency label
    if total_harsh_count == 0:
        frequency_label = "No usage"
    elif total_harsh_count >= 10:
        frequency_label = "Saturated"
    elif total_harsh_count >= 6:
        frequency_label = "High frequency"
    elif total_harsh_count >= 3:
        frequency_label = "Moderate frequency"
    else:
        frequency_label = "Low frequency"
    
    # Calculate 1-10 severity score based on harsh word frequency
    if total_harsh_count == 0:
        severity_score = 0
    else:
        # Scale harsh word count to 1-10 range
        severity_score = min(10, max(1, int((total_harsh_count / 10) * 10)))
    
    # Create string of harsh words found
    harsh_words_found = ", ".join([f"{word}({count})" for word, count in harsh_word_counts.items()]) if harsh_word_counts else "None"

    return (index, word_count, error_count, trust, frequency_label, harsh_words_found, severity_score)