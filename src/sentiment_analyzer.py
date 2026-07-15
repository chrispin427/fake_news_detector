import logging

try:
    from textblob import TextBlob
    _HAS_TEXTBLOB = True
    _TEXTBLOB_ERROR = None
except (ImportError, LookupError) as e:
    _HAS_TEXTBLOB = False
    _TEXTBLOB_ERROR = str(e)

logger = logging.getLogger("sentiment_analyzer")

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


def _ensure_nltk_data():
    """Auto-download required NLTK corpora if missing."""
    import nltk
    # Map resource names to their expected nltk.data.find paths
    _RESOURCE_PATHS = {
        "punkt": "tokenizers/punkt",
        "averaged_perceptron_tagger": "taggers/averaged_perceptron_tagger",
        "wordnet": "corpora/wordnet",
        "brown": "corpora/brown",
    }
    for resource, expected_path in _RESOURCE_PATHS.items():
        try:
            nltk.data.find(expected_path)
        except LookupError:
            try:
                logger.info("Downloading missing NLTK data: %s", resource)
                nltk.download(resource, quiet=True)
            except Exception:
                pass


def analyze_sentiment(text):

    if not _HAS_TEXTBLOB:
        logger.warning("TextBlob not available (%s). Trying to download NLTK data...", _TEXTBLOB_ERROR)
        try:
            _ensure_nltk_data()
            from textblob import TextBlob as tb
            blob = tb(text)
        except Exception as fallback_err:
            logger.warning("Sentiment analysis unavailable after NLTK data download: %s", fallback_err)
            return {
                "polarity": 0.0,
                "sensational_words": [],
                "manipulation_risk": "Low",
            }
    else:
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