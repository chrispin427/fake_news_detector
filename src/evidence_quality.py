"""
src/evidence_quality.py

Evaluates the credibility of supporting evidence by scoring each
evidence source against the publisher reputation system defined in
src/source_rating.py.  Deduplicates sources before scoring so that
multiple articles from the same publisher do not inflate the result.

Typical usage:
    from src.evidence_quality import compute_evidence_quality
    quality = compute_evidence_quality(evidence)
    # -> {"score": 92, "label": "Excellent", "source_count": 5,
    #     "breakdown": {"reuters.com": 98, "bbc.com": 95, ...}}
"""

import logging

from src.source_rating import SOURCE_SCORES

logger = logging.getLogger("evidence_quality")

# ---------------------------------------------------------------------------
# PUBLISHER NAME - DOMAIN MAPPING
# ---------------------------------------------------------------------------

PUBLISHER_NAME_MAP = {
    "reuters": "reuters.com",
    "reuters news": "reuters.com",
    "associated press": "apnews.com",
    "ap": "apnews.com",
    "the associated press": "apnews.com",
    "bbc": "bbc.com",
    "bbc news": "bbc.com",
    "bbc.com": "bbc.com",
    "bbc news online": "bbc.com",
    "bbc monitoring": "bbc.com",
    "npr": "npr.org",
    "npr news": "npr.org",
    "the guardian": "theguardian.com",
    "guardian": "theguardian.com",
    "the new york times": "nytimes.com",
    "new york times": "nytimes.com",
    "nytimes.com": "nytimes.com",
    "the washington post": "washingtonpost.com",
    "washington post": "washingtonpost.com",
    "bloomberg": "bloomberg.com",
    "bloomberg news": "bloomberg.com",
    "bloomberg.com": "bloomberg.com",
    "wall street journal": "wsj.com",
    "wsj": "wsj.com",
    "wsj.com": "wsj.com",
    "financial times": "ft.com",
    "ft": "ft.com",
    "ft.com": "ft.com",
    "al jazeera": "aljazeera.com",
    "aljazeera.com": "aljazeera.com",
    "al jazeera english": "aljazeera.com",
    "the economist": "economist.com",
    "economist": "economist.com",
    "dw": "dw.com",
    "deutsche welle": "dw.com",
    "france 24": "france24.com",
    "france24": "france24.com",
    "agence france presse": "afp.com",
    "afp": "afp.com",
    "pbs": "pbs.org",
    "pbs newshour": "pbs.org",
    "cnn": "cnn.com",
    "cnn.com": "cnn.com",
    "abc news": "abcnews.go.com",
    "abc": "abcnews.go.com",
    "abcnews": "abcnews.go.com",
    "cbs news": "cbsnews.com",
    "nbc news": "nbcnews.com",
    "nbcnews.com": "nbcnews.com",
    "forbes": "forbes.com",
    "forbes.com": "forbes.com",
    "usa today": "usatoday.com",
    "politico": "politico.com",
    "the hill": "thehill.com",
    "newsweek": "newsweek.com",
    "fox news": "foxnews.com",
    "foxnews.com": "foxnews.com",
    "fox business": "foxnews.com",
    "los angeles times": "latimes.com",
    "la times": "latimes.com",
    "chicago tribune": "chicagotribune.com",
    "le monde": "lemonde.fr",
    "lemonde.fr": "lemonde.fr",
    "the independent": "independent.co.uk",
    "independent": "independent.co.uk",
    "the telegraph": "telegraph.co.uk",
    "telegraph": "telegraph.co.uk",
    "the times": "thetimes.co.uk",
    "the sunday times": "thetimes.co.uk",
    "irishtimes.com": "irishtimes.com",
    "the irish times": "irishtimes.com",
    "sydney morning herald": "smh.com.au",
    "the age": "theage.com.au",
    "south china morning post": "scmp.com",
    "scmp": "scmp.com",
    "japantimes.co.jp": "japantimes.co.jp",
    "the japan times": "japantimes.co.jp",
    "straits times": "straitstimes.com",
    "times of india": "timesofindia.indiatimes.com",
    "the times of india": "timesofindia.indiatimes.com",
    "the hindu": "hindu.com",
    "hindu": "hindu.com",
    "al-monitor": "al-monitor.com",
    "middle east eye": "middleeasteye.net",
    "nation.africa": "nation.africa",
    "daily nation": "nation.africa",
    "africanews": "africanews.com",
    "africanews.com": "africanews.com",
    "mail & guardian": "mg.co.za",
    "news24": "news24.com",
    "the citizen": "citizen.co.za",
    "the east african": "theeastafrican.co.ke",
    "business daily africa": "businessdailyafrica.com",
    "the observer": "observer.ug",
    "guardian.ng": "guardian.ng",
    "the guardian nigeria": "guardian.ng",
    "premium times": "premiumtimesng.com",
    "allafrica": "allafrica.com",
    "abc.net.au": "abc.net.au",
    "abc australia": "abc.net.au",
    "cbc": "cbc.ca",
    "cbc news": "cbc.ca",
    "channel 4": "channel4.com",
    "itv": "itv.com",
    "itv news": "itv.com",
    "sky news": "skynews.com",
    "euronews": "euronews.com",
    "ndtv": "ndtv.com",
    "haaretz": "haaretz.com",
    "ynet": "ynetnews.com",
    "times of israel": "timesofisrael.com",
    "jpost": "jpost.com",
    "the jerusalem post": "jpost.com",
    "daily mail": "dailymail.co.uk",
    "dailymail.co.uk": "dailymail.co.uk",
    "the sun": "the-sun.com",
    "the sun uk": "the-sun.com",
    "new york post": "nypost.com",
    "nypost": "nypost.com",
    "spectator": "spectator.co.uk",
    "the spectator": "spectator.co.uk",
    "the atlantic": "theatlantic.com",
    "the new yorker": "newyorker.com",
    "new yorker": "newyorker.com",
    "slate": "slate.com",
    "vox": "vox.com",
    "buzzfeed": "buzzfeednews.com",
    "buzzfeed news": "buzzfeednews.com",
    "huffpost": "huffpost.com",
    "huffington post": "huffpost.com",
    "facebook": "facebook.com",
    "instagram": "instagram.com",
    "x": "x.com",
    "twitter": "twitter.com",
    "tiktok": "tiktok.com",
    "youtube": "youtube.com",
    "google news": "google.com",
}

QUALITY_LABELS = [
    (90, "Excellent"),
    (75, "High"),
    (60, "Moderate"),
    (40, "Weak"),
    (0,  "Poor"),
]


def _normalise_source(src):
    """Normalise a raw evidence source value to a lowercase string."""
    if isinstance(src, dict):
        src = src.get("name", str(src))
    if src is None:
        return "unknown"
    return str(src).strip().lower()


def _lookup_publisher_score(source_name):
    """
    Look up a publisher's reputation score by name or domain.

    Tries: direct domain match, name-via-PUBLISHER_NAME_MAP, suffix
    stripping, and bare-name + TLD fallback.  Returns None when no
    match is found.
    """
    name = source_name.lower().strip()
    if name in SOURCE_SCORES:
        return SOURCE_SCORES[name]
    if name in PUBLISHER_NAME_MAP:
        domain = PUBLISHER_NAME_MAP[name]
        if domain in SOURCE_SCORES:
            return SOURCE_SCORES[domain]
    for suffix in (" news", " online", " uk", " us", " international", ".com"):
        if name.endswith(suffix):
            stripped = name[: -len(suffix)]
            if stripped in PUBLISHER_NAME_MAP:
                domain = PUBLISHER_NAME_MAP[stripped]
                if domain in SOURCE_SCORES:
                    return SOURCE_SCORES[domain]
    if "." not in name:
        for tld in (".com", ".org", ".co.uk", ".net"):
            candidate = name + tld
            if candidate in SOURCE_SCORES:
                return SOURCE_SCORES[candidate]
    return None


def compute_evidence_quality(evidence):
    """
    Evaluate the credibility of supporting evidence.

    Deduplicates multiple articles from the same publisher so the score
    reflects the QUALITY of sources rather than mere QUANTITY.

    Args:
        evidence: List of dicts, each with at least a "source" key.

    Returns:
        dict with:
          - score (int 0-100): average reputation of unique sources
          - label (str): quality classification
          - source_count (int): number of unique sources identified
          - breakdown (dict): {source_name: score} for each unique source
          - unmatched (list): sources that could not be scored
    """
    sep_line = "=" * 60
    logger.info("")
    logger.info(sep_line)
    logger.info("  EVIDENCE QUALITY SCORING")
    logger.info(sep_line)
    logger.info("  Total evidence items: %d", len(evidence) if evidence else 0)

    if not evidence:
        logger.info("  -> No evidence to score")
        logger.info(sep_line)
        return {
            "score": 0,
            "label": "Poor",
            "source_count": 0,
            "breakdown": {},
            "unmatched": [],
        }

    # Deduplicate: collect unique source names
    unique_sources = {}
    for item in evidence:
        raw = item.get("source", "Unknown")
        normalised = _normalise_source(raw)
        if normalised not in unique_sources:
            unique_sources[normalised] = raw

    logger.info("  Unique sources identified: %d", len(unique_sources))

    # Score each unique source
    breakdown = {}
    unmatched = []
    all_scores = []

    for normalised_name, display_name in unique_sources.items():
        score = _lookup_publisher_score(normalised_name)
        if score is not None:
            all_scores.append(score)
            breakdown[str(display_name)] = score
            logger.info("    [%s] -> score=%s", str(display_name)[:40], score)
        else:
            unmatched.append(display_name)
            logger.info("    [%s] -> UNMATCHED (default 50)", str(display_name)[:40])

    # Compute average — unmatched sources get a neutral score of 50
    if all_scores:
        avg = round(sum(all_scores) / len(all_scores))
    else:
        avg = 50

    if unmatched:
        total_scores = all_scores + [50] * len(unmatched)
        avg = round(sum(total_scores) / len(total_scores))
        logger.info("  Blended with %d unmatched source(s) at score=50", len(unmatched))

    avg = max(0, min(100, avg))

    # Classify
    label = "Poor"
    for threshold, lbl in QUALITY_LABELS:
        if avg >= threshold:
            label = lbl
            break

    logger.info("  Average quality score: %s/100", avg)
    logger.info("  Quality classification: %s", label)
    logger.info("  Unique source count:    %d", len(unique_sources))
    logger.info(sep_line)

    return {
        "score": avg,
        "label": label,
        "source_count": len(unique_sources),
        "breakdown": breakdown,
        "unmatched": unmatched,
    }
