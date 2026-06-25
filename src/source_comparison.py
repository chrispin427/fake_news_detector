from difflib import SequenceMatcher


def compare_sources(claim, evidence_articles):
    """
    Compare a detected claim against evidence article titles
    to determine how strongly different news sources agree.

    Args:
        claim: The extracted claim string.
        evidence_articles: List of dicts with "title" key.

    Returns:
        dict with agreement (int), classification (str),
        and sources_checked (int).
    """

    if not evidence_articles or not claim:
        return {
            "agreement": 0,
            "classification": "Low Agreement",
            "sources_checked": 0
        }

    similarities = []
    claim_lower = claim.lower()

    for item in evidence_articles:
        source_title = item.get("title", "").lower()
        if not source_title:
            continue
        similarity = SequenceMatcher(
            None,
            claim_lower,
            source_title
        ).ratio()
        similarities.append(similarity)

    if not similarities:
        return {
            "agreement": 0,
            "classification": "Low Agreement",
            "sources_checked": 0
        }

    avg_similarity = (
        sum(similarities) / len(similarities)
    ) * 100
    agreement = round(avg_similarity)

    if agreement >= 70:
        classification = "High Agreement"
    elif agreement >= 40:
        classification = "Moderate Agreement"
    else:
        classification = "Low Agreement"

    return {
        "agreement": agreement,
        "classification": classification,
        "sources_checked": len(evidence_articles)
    }