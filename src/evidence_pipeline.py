"""
src/evidence_pipeline.py

Shared evidence-retrieval pipeline used by both app/app.py and
src/debug_audit.py.  Guarantees that both paths construct queries,
retrieve evidence, and handle fallbacks in exactly the same way,
eliminating the divergence that could otherwise produce different
verdicts for the same article.
"""

import logging

logger = logging.getLogger("evidence_pipeline")


def build_evidence_query(article_title, text_to_analyze, claim_text=None):
    """
    Build the evidence search query consistently across all callers.
    Priority: 1. Article title, 2. Claim text, 3. First 10 words of body
    """
    has_real_title = bool(article_title) and article_title not in (
        "User-Submitted Text",
        "Untitled Article",
        "Untitled Article (Search Fallback)",
        "N/A",
        "",
    )
    if has_real_title:
        logger.info("  [EvidencePipeline] Using article title as query: %s", article_title[:100])
        return article_title
    if claim_text and len(claim_text.strip()) >= 10:
        logger.info("  [EvidencePipeline] Using claim text as query (length=%d)", len(claim_text))
        return claim_text
    fallback = " ".join(text_to_analyze.split()[:10]) if text_to_analyze else ""
    logger.info("  [EvidencePipeline] Using text fallback as query: %s", fallback[:100])
    return fallback


def retrieve_evidence(evidence_query, fallback_results=None):
    """
    Retrieve evidence and optionally supplement with search fallback results.
    """
    from src.evidence_finder import find_evidence
    evidence = find_evidence(evidence_query)
    if fallback_results:
        existing_urls = {e.get("url", "").lower().rstrip("/") for e in evidence if e.get("url")}
        added = 0
        for fb in fallback_results:
            fb_url = fb.get("link", "").lower().rstrip("/")
            if fb_url and fb_url not in existing_urls:
                evidence.append({
                    "source": "Web Search",
                    "title": fb.get("title", ""),
                    "url": fb.get("link", ""),
                })
                existing_urls.add(fb_url)
                added += 1
        if added:
            logger.info("  [EvidencePipeline] Supplemented with %d fallback results", added)
    return evidence


def normalise_source(src):
    """Handle source being a string, dict, or None consistently."""
    if isinstance(src, dict):
        return src.get("name", str(src))
    if src is None:
        return "Unknown"
    return str(src)


def build_results_dict(evidence):
    """Build backward-compatible results dict from evidence source counts."""
    src_counts = {}
    for item in evidence:
        s = normalise_source(item.get("source"))
        src_counts[str(s)] = src_counts.get(str(s), 0) + 1
    return src_counts


def compute_evidence_quality(evidence):
    """
    Evaluate the quality of supporting evidence using the publisher
    reputation system.  Delegates to src.evidence_quality so every
    consumer of the shared pipeline gets consistent quality scores.

    Logs detailed debug output via the evidence_quality logger.

    Args:
        evidence: List of dicts with at least a "source" key.

    Returns:
        dict with score (0-100), label, source_count, breakdown, unmatched.
    """
    from src.evidence_quality import compute_evidence_quality as _compute
    result = _compute(evidence)
    logger.info("  [EvidencePipeline] Evidence Quality: %s/100 (%s) across %d unique source(s)",
                result["score"], result["label"], result["source_count"])
    return result
