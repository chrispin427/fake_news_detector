"""
src/fact_checker.py

Determines whether an extracted claim is Supported, Partially Supported,
Unsupported, or Unverified using evidence already gathered by the
evidence retrieval layer (src.evidence_finder.py).

This module does NOT make its own API calls. All evidence is provided
by the caller, eliminating redundant searches.

Pipeline flow:
    Article -> Claim Extraction -> Evidence Finder -> Fact Checker
"""

import logging
from difflib import SequenceMatcher

logger = logging.getLogger("fact_checker")


def fact_check(text, evidence=None):
    from src.claim_extractor import extract_claim
    from src.entity_extractor import extract_entities

    claim = extract_claim(text)
    entities = extract_entities(claim)

    sep_line = "=" * 60
    logger.info("")
    logger.info(sep_line)
    logger.info("  FACT CHECK - Evidence-Based Verdict")
    logger.info(sep_line)
    logger.info("  Claim: %s", claim[:200])

    if evidence is None:
        evidence = []

    ev_count = len(evidence)
    logger.info("  Evidence items received: %d", ev_count)

    if ev_count == 0:
        logger.info("  -> No evidence available - verdict: Unverified")
        logger.info(sep_line)
        return {"claim": claim, "verdict": "Unverified", "sources": 0, "total_evidence": 0, "results": {}, "entities": entities}

    matching = []
    match_scores = []

    # Normalise source to string (SerpAPI can return source as dict)
    def _normalise(src):
        if isinstance(src, dict):
            return src.get("name", str(src))
        return str(src) if src is not None else "Unknown"

    for item in evidence:
        title = item.get("title", "")
        source = _normalise(item.get("source"))
        item["_source_str"] = source  # cache for results dict
        if not title:
            continue
        sim = SequenceMatcher(None, claim.lower(), title.lower()).ratio()
        match_scores.append((sim, source, title))
        if sim >= 0.25:
            matching.append(item)

    match_scores.sort(reverse=True, key=lambda x: x[0])
    for sim, source, title in match_scores:
        label = "V" if sim >= 0.25 else "X"
        logger.info("  %s [%s] sim=%.2f - %s", label, source, sim, title[:100])

    matched_count = len(matching)
    match_pct = round(matched_count / ev_count * 100, 1) if ev_count > 0 else 0.0
    logger.info("  Matching evidence: %d / %d (%s%%)", matched_count, ev_count, match_pct)

    if matched_count >= 3:
        verdict = "Supported"
    elif matched_count >= 1:
        verdict = "Partially Supported"
    elif ev_count > 0:
        verdict = "Unsupported"
    else:
        verdict = "Unverified"

    logger.info("  Verdict: %s", verdict)

    # Build backward-compatible results dict
    results = {}
    for item in evidence:
        src = item.get("_source_str", "Unknown")
        results[src] = 0
    for item in matching:
        src = item.get("_source_str", "Unknown")
        results[src] = results.get(src, 0) + 1

    logger.info(sep_line)

    return {"claim": claim, "verdict": verdict, "sources": matched_count, "total_evidence": ev_count, "results": results, "entities": entities}
