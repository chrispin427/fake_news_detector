import re


def extract_claim(text):
    """
    Extract the most newsworthy claim from an article.
    Version 1.
    """

    if not text:
        return ""

    # Split into sentences
    sentences = re.split(r'[.!?]+', text)

    # Remove empty sentences
    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    if not sentences:
        return text[:300]

    keywords = [
        "announced",
        "confirmed",
        "reported",
        "claims",
        "claim",
        "says",
        "said",
        "revealed",
        "warned",
        "approved",
        "arrested",
        "killed",
        "dead",
        "dies",
        "won",
        "elected",
        "signed",
        "launches",
        "launched",
        "discovers",
        "discovered",
        "found",
        "breaking"
    ]

    scored_sentences = []

    for sentence in sentences:

        score = 0

        sentence_lower = sentence.lower()

        # Keyword scoring
        for keyword in keywords:
            if keyword in sentence_lower:
                score += 5

        # Prefer medium-length sentences
        length = len(sentence.split())

        if 8 <= length <= 40:
            score += 3

        # Earlier sentences are usually important
        position_bonus = max(
            0,
            10 - sentences.index(sentence)
        )

        score += position_bonus

        scored_sentences.append(
            (score, sentence)
        )

    scored_sentences.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return scored_sentences[0][1]