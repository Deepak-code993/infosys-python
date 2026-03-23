"""
rule_engine.py — Harsh word detection + Sentiment scoring engine.

Sentiment logic:
  - Handles modifiers: "not X" flips polarity, "very X" amplifies
  - Counts repeated words correctly: "good good bad" -> pos=2, neg=1
  - Returns positive_count, negative_count, neutral_count, final_sentiment
"""

import re

# ── Harsh words ──────────────────────────────────────────────────────────────
HARSH_WORDS = [
    'murder', 'rape', 'suicide', 'homicide',
    'genocide', 'assassination', 'abuse', 'molestation'
]

# ── Sentiment word lists ──────────────────────────────────────────────────────
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
    'outstanding', 'brilliant', 'superb', 'perfect', 'love', 'loved',
    'happy', 'happiness', 'joy', 'joyful', 'positive', 'best', 'better',
    'awesome', 'nice', 'beautiful', 'splendid', 'magnificent', 'pleasant',
    'delightful', 'impressive', 'remarkable', 'exceptional', 'fine',
    'helpful', 'useful', 'effective', 'efficient', 'strong', 'powerful',
    'safe', 'secure', 'clean', 'clear', 'smart', 'intelligent', 'wise',
    'kind', 'generous', 'honest', 'loyal', 'brave', 'confident', 'calm',
    'peaceful', 'successful', 'victory', 'win', 'winning', 'progress',
    'improve', 'improvement', 'benefit', 'gain', 'profit', 'reward',
    'support', 'trust', 'hope', 'inspire', 'motivated', 'energetic'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'horrible', 'awful', 'dreadful', 'poor', 'worst',
    'worse', 'hate', 'hated', 'sad', 'sadness', 'angry', 'anger', 'fear',
    'fearful', 'negative', 'evil', 'disgusting', 'nasty', 'ugly', 'painful',
    'pain', 'suffer', 'suffering', 'problem', 'trouble', 'difficult',
    'difficulty', 'failure', 'fail', 'failed', 'lose', 'loss', 'damage',
    'dangerous', 'harmful', 'toxic', 'corrupt', 'corrupt', 'broken',
    'wrong', 'error', 'mistake', 'fault', 'blame', 'weak', 'useless',
    'ineffective', 'inefficient', 'boring', 'dull', 'stupid', 'foolish',
    'reckless', 'lazy', 'careless', 'rude', 'cruel', 'violent', 'threat',
    'threaten', 'attack', 'destroy', 'destruction', 'waste', 'reject',
    'rejected', 'denied', 'deny', 'unfair', 'unjust', 'dishonest',
    'deceptive', 'mislead', 'misleading', 'fraud', 'corrupt', 'shame'
}

NEGATION_WORDS = {'not', 'no', 'never', 'neither', 'nor', 'nobody', 'nothing',
                  'nowhere', 'hardly', 'barely', 'scarcely', "n't", 'cannot', "can't",
                  "won't", "don't", "doesn't", "didn't", "isn't", "aren't",
                  "wasn't", "weren't", "shouldn't", "wouldn't", "couldn't"}

AMPLIFIER_WORDS = {'very', 'extremely', 'highly', 'absolutely', 'totally',
                   'completely', 'utterly', 'deeply', 'strongly', 'really',
                   'incredibly', 'remarkably', 'exceptionally', 'particularly'}


def _tokenize(text):
    """Lowercase and split into word tokens."""
    return re.findall(r"[a-z']+", text.lower())


def score_sentiment(text):
    """
    Analyse text for sentiment.

    Returns:
        positive_count  (int) — number of positive word hits (with amplifiers = 2)
        negative_count  (int) — number of negative word hits
        neutral_count   (int) — words that are neither positive nor negative
        final_sentiment (str) — "Positive" / "Negative" / "Neutral"
        details         (dict) — word-level breakdown for transparency
    """
    if not text or not text.strip():
        return 0, 0, 0, "Neutral", {}

    tokens = _tokenize(text)
    if not tokens:
        return 0, 0, 0, "Neutral", {}

    positive_count = 0
    negative_count = 0
    word_details = {}   # word -> net contribution

    total_tokens = len(tokens)
    i = 0

    while i < total_tokens:
        token = tokens[i]

        # Look back for negation (window = 3 words)
        negated = False
        for j in range(max(0, i - 3), i):
            if tokens[j] in NEGATION_WORDS:
                negated = True
                break

        # Look back for amplifier (window = 2 words)
        amplified = False
        for j in range(max(0, i - 2), i):
            if tokens[j] in AMPLIFIER_WORDS:
                amplified = True
                break

        weight = 2 if amplified else 1

        if token in POSITIVE_WORDS:
            if negated:
                negative_count += weight
                word_details[token] = word_details.get(token, 0) - weight
            else:
                positive_count += weight
                word_details[token] = word_details.get(token, 0) + weight

        elif token in NEGATIVE_WORDS:
            if negated:
                positive_count += weight
                word_details[token] = word_details.get(token, 0) + weight
            else:
                negative_count += weight
                word_details[token] = word_details.get(token, 0) - weight

        i += 1

    # Count neutral tokens (not in either list, not stop-words)
    SKIP = NEGATION_WORDS | AMPLIFIER_WORDS | {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'about',
        'into', 'from', 'as', 'it', 'its', 'this', 'that', 'these',
        'those', 'and', 'or', 'but', 'so', 'if', 'then', 'when',
        'where', 'who', 'which', 'what', 'how', 'i', 'you', 'he',
        'she', 'we', 'they', 'my', 'your', 'his', 'her', 'our',
        'their', 'me', 'him', 'us', 'them'
    }
    neutral_count = sum(
        1 for t in tokens
        if t not in POSITIVE_WORDS and t not in NEGATIVE_WORDS and t not in SKIP
    )

    # Final verdict
    if positive_count > negative_count:
        final_sentiment = "Positive"
    elif negative_count > positive_count:
        final_sentiment = "Negative"
    else:
        final_sentiment = "Neutral"

    return positive_count, negative_count, neutral_count, final_sentiment, word_details


def process_chunk(data):
    """
    Process one chunk (used by ThreadPoolExecutor).
    Accepts (index, chunk) or (index, source_file, chunk).
    Returns a unified result tuple.
    """
    if len(data) == 3:
        index, source_file, chunk = data
    else:
        index, chunk = data
        source_file = "unknown"

    text = "".join(chunk)

    # ── Basic counts ─────────────────────────────────────────────────────────
    word_count = len(text.split())
    error_count = text.lower().count("error")

    # ── Trust ────────────────────────────────────────────────────────────────
    if error_count == 0:
        trust = "Trustable"
    elif error_count <= 5:
        trust = "Moderately Trustable"
    else:
        trust = "Not Trustable"

    # ── Harsh words ──────────────────────────────────────────────────────────
    lower_text = text.lower()
    harsh_word_counts = {}
    total_harsh_count = 0

    for word in HARSH_WORDS:
        count = lower_text.count(word)
        if count > 0:
            harsh_word_counts[word] = count
            total_harsh_count += count

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

    severity_score = 0 if total_harsh_count == 0 else min(10, max(1, int((total_harsh_count / 10) * 10)))

    harsh_words_found = (
        ", ".join([f"{w}({c})" for w, c in harsh_word_counts.items()])
        if harsh_word_counts else "None"
    )

    # ── Sentiment ────────────────────────────────────────────────────────────
    positive_count, negative_count, neutral_count, final_sentiment, word_details = score_sentiment(text)

    return (
        index,
        source_file,
        word_count,
        error_count,
        trust,
        frequency_label,
        harsh_words_found,
        severity_score,
        positive_count,
        negative_count,
        neutral_count,
        final_sentiment,
        str(word_details),   # stored as string in DB
    )
