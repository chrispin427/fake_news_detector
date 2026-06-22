from difflib import SequenceMatcher


def calculate_similarity(text1, text2):
    """
    Compare two pieces of text and return
    similarity percentage.
    """

    if not text1 or not text2:
        return 0

    score = SequenceMatcher(
        None,
        text1.lower(),
        text2.lower()
    ).ratio()

    return round(score * 100, 2)