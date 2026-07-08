from difflib import SequenceMatcher


def detect_rewrite(claim, evidence_articles):
    """
    Determine whether an article's claim appears manipulated,
    rewritten, or altered compared to trusted evidence sources.

    Compares the extracted claim against evidence article titles
    using similarity scoring.

    Returns "Unknown" risk with a neutral explanation when there
    are insufficient supporting articles to perform a meaningful
    comparison.  This prevents evidence-retrieval failures from
    being falsely flagged as manipulation.
    """

    if not claim or not evidence_articles:
        return {
            "similarity": 0.0,
            "risk": "Unknown",
            "explanation": "No evidence available for comparison - manipulation risk cannot be assessed."
        }

    similarities = []
    claim_lower = claim.lower()

    for item in evidence_articles:
        source_title = item.get("title", "").lower()
        if not source_title:
            continue
        similarity = SequenceMatcher(None, claim_lower, source_title).ratio()
        similarities.append(similarity)

    if not similarities:
        return {
            "similarity": 0.0,
            "risk": "Unknown",
            "explanation": "No comparable evidence titles found - manipulation risk cannot be assessed."
        }

    avg_similarity = round((sum(similarities) / len(similarities)) * 100, 2)

    if avg_similarity >= 70:
        risk = "Low"
        explanation = "The claim closely matches trusted news sources. Low likelihood of manipulation."
    elif avg_similarity >= 50:
        risk = "Medium"
        explanation = "The claim partially matches trusted sources. Some details may have been altered or rephrased."
    else:
        risk = "High"
        explanation = "The claim differs significantly from trusted sources. High likelihood of rewriting or fabrication."

    return {"similarity": avg_similarity, "risk": risk, "explanation": explanation}
