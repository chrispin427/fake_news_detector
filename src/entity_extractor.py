import spacy
import re
import sys

# Load spaCy model with graceful fallback
try:
    nlp = spacy.load("en_core_web_sm")
    _model_loaded = True
except (IOError, OSError):
    print(
        "Warning: spaCy model 'en_core_web_sm' not found. "
        "Run: python -m spacy download en_core_web_sm",
        file=sys.stderr
    )
    _model_loaded = False
    nlp = None


# Fallback: simple regex-based entity extraction when spaCy model is missing
_SIMPLE_PATTERNS = {
    "people": [
        r"[A-Z][a-z]+ [A-Z][a-z]+",  # Capitalized Name
    ],
    "dates": [
        r"\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}",
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}",
        r"\d{4}-\d{2}-\d{2}",
        r"(?:yesterday|today|tomorrow|last\s+week|next\s+week|last\s+month|next\s+month)",
    ],
}


def extract_entities(text):
    """
    Extract named entities from text.
    Falls back to simple pattern matching if spaCy model unavailable.
    """

    entities = {
        "people": [],
        "organizations": [],
        "locations": [],
        "dates": []
    }

    if _model_loaded and nlp is not None:
        # Use spaCy NER
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["people"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ in ("GPE", "LOC"):
                entities["locations"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
    else:
        # Fallback: basic pattern matching
        for match in re.finditer(_SIMPLE_PATTERNS["people"][0], text):
            name = match.group().strip()
            if name not in entities["people"]:
                entities["people"].append(name)
        for pattern in _SIMPLE_PATTERNS["dates"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_str = match.group().strip()
                if date_str not in entities["dates"]:
                    entities["dates"].append(date_str)

    # Remove duplicates (also handles spaCy duplicates)
    for key in entities:
        seen = set()
        unique = []
        for item in entities[key]:
            lower = item.lower()
            if lower not in seen:
                seen.add(lower)
                unique.append(item)
        entities[key] = unique

    return entities