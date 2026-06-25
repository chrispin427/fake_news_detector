from textblob import TextBlob

SENSATIONAL_WORDS = [
    "shocking",
    "explosive",
    "unbelievable",
    "secret",
    "exposed",
    "scandal",
    "urgent",
    "warning",
    "breaking",
    "must see",
    "viral",
    "destroyed",
    "terrifying",
    "panic",
    "disaster"
]


def analyze_sentiment(text):

    blob = TextBlob(text)

    polarity = blob.sentiment.polarity

    found_words = []

    text_lower = text.lower()

    for word in SENSATIONAL_WORDS:

        if word in text_lower:
            found_words.append(word)

    if len(found_words) >= 3:
        risk = "High"

    elif len(found_words) >= 1:
        risk = "Medium"

    else:
        risk = "Low"

    return {
        "polarity": round(polarity, 2),
        "sensational_words": found_words,
        "manipulation_risk": risk
    }