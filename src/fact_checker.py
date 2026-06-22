from src.news_api import verify_news
from src.claim_extractor import extract_claim
from src.entity_extractor import extract_entities


def fact_check(text):

    claim = extract_claim(text)
    entities = extract_entities(claim)

    results, total = verify_news(claim)

    matched_sources = sum(
        1 for value in results.values()
        if value > 0
    )

    if matched_sources >= 3:
        verdict = "Supported"

    elif matched_sources >= 1:
        verdict = "Partially Supported"

    else:
        verdict = "Unverified"

    return {
        "claim": claim,
        "verdict": verdict,
        "sources": matched_sources,
        "results": results,
        "entities": entities
    }