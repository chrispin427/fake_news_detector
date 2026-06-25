import re


CLICKBAIT_PHRASES = [
    "you won't believe",
    "will never believe",
    "can't believe",
    "what happens next",
    "you need to see",
    "must see",
    "don't want you to know",
    "they don't want you",
    "the truth about",
    "what happened next",
    "left speechless",
    "mind blown",
    "blown away",
    "one weird trick",
    "doctors hate",
    "this is why",
    "here's why",
    "the reason why",
    "number one",
    "top 10",
    "will shock you",
    "changed forever"
]

SHOCK_WORDS = [
    "shocking", "shock", "horrifying", "terrifying",
    "devastating", "appalling", "outrageous", "scandalous",
    "explosive", "bombshell", "jaw-dropping", "stunning",
    "unbelievable", "incredible", "astonishing", "astounding",
    "mind-boggling", "earth-shattering", "shattering",
    "dramatic", "sensational", "alarming", "disturbing"
]

EMOTIONAL_WORDS = [
    "heartbreaking", "tearjerker", "crying",
    "tears", "emotional", "inspiring", "heroic", "tragic",
    "miracle", "miraculous", "desperate", "terrified",
    "furious", "outraged", "devastated", "heartwarming",
    "gut-wrenching", "soul-crushing", "rage", "fear"
]

URGENCY_PHRASES = [
    "breaking news", "breaking", "urgent", "just in",
    "developing story", "developing", "alert", "update",
    "immediately", "right now", "act now", "don't wait",
    "last chance", "final warning", "emergency", "critical",
    "happening now", "moment's notice", "now or never",
    "limited time"
]


def analyze_headline(headline):
    """
    Analyze a headline for sensationalized, clickbait,
    emotionally manipulative, misleading, or exaggerated content.

    Checks:
    - Excessive capitalization
    - Multiple exclamation marks
    - Clickbait phrases
    - Shock words
    - Emotional manipulation words
    - Urgency phrases

    Args:
        headline: The headline string to analyze.

    Returns:
        dict with headline (str), risk (str),
        score (int), and reasons (list).
    """

    score = 0
    reasons = []
    text = headline.lower()

    # --- Excessive capitalization ---
    upper_count = sum(1 for c in headline if c.isupper())
    if len(headline) > 0 and upper_count / len(headline) > 0.6:
        score += 20
        reasons.append("Excessive capitalization (" + str(upper_count) + " uppercase letters)")

    if headline.isupper():
        score += 10  # Additional penalty for full caps
        reasons.append("Headline is entirely in uppercase")

    # --- Multiple exclamation marks ---
    exclamation_count = headline.count("!")
    if exclamation_count > 0:
        exclamation_score = min(exclamation_count * 8, 25)
        score += exclamation_score
        if exclamation_count == 1:
            reasons.append("Contains exclamation mark")
        else:
            reasons.append("Contains " + str(exclamation_count) + " exclamation marks")

    # --- Question marks (rhetorical) ---
    question_count = headline.count("?")
    if question_count > 0:
        score += min(question_count * 5, 10)
        reasons.append("Contains " + str(question_count) + " question mark(s)")

    # --- Clickbait phrases ---
    for phrase in CLICKBAIT_PHRASES:
        if phrase in text:
            score += 12
            reasons.append("Clickbait phrase detected: \"" + phrase + "\"")

    # --- Shock words ---
    for word in SHOCK_WORDS:
        if word in text:
            score += 8
            reasons.append("Shock word detected: \"" + word + "\"")

    # --- Emotional manipulation words ---
    for word in EMOTIONAL_WORDS:
        if word in text:
            score += 6
            reasons.append("Emotional manipulation word: \"" + word + "\"")

    # --- Urgency phrases (with overlap prevention) ---
    matched_ranges = []
    sorted_urgency = sorted(URGENCY_PHRASES, key=len, reverse=True)
    for phrase in sorted_urgency:
        pos = text.find(phrase)
        if pos == -1:
            continue
        start = pos
        end = pos + len(phrase)
        overlaps = any(
            not (end <= r[0] or start >= r[1])
            for r in matched_ranges
        )
        if not overlaps:
            matched_ranges.append((start, end))
            score += 10
            reasons.append("Urgency phrase detected: \"" + phrase + "\"")

    # --- All caps words (individual words in ALL CAPS) ---
    words = headline.split()
    all_caps_words = [w for w in words if w.isupper() and len(w) > 1]
    if len(all_caps_words) > 1 and not headline.isupper():
        score += len(all_caps_words) * 3
        reasons.append(str(len(all_caps_words)) + " words in ALL CAPS: " + ", ".join(all_caps_words))

    # --- Deduplicate reasons ---
    seen = set()
    unique_reasons = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)
    reasons = unique_reasons

    # Clamp score to 0-100
    score = max(0, min(score, 100))

    # --- Risk classification ---
    if score >= 40:
        risk = "High"
    elif score >= 15:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "headline": headline,
        "risk": risk,
        "score": score,
        "reasons": reasons
    }