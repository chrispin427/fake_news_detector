"""
src/source_rating.py

Source reputation scoring with canonical domain resolution and expanded
publisher coverage.

Integrates with:
  - canonical_domain.py for resolving shortened URLs, redirects, mobile
    subdomains, and regional variants to their parent publisher domain
  - dynamic_reputation.py for advanced reputation signals (domain age,
    HTTPS validity, historical evidence reliability, etc.)

Usage:
    from src.source_rating import get_source_rating
    rating = get_source_rating("https://aje.news/abc123")
"""

from urllib.parse import urlparse

# Import canonical domain resolution - gracefully handles missing module
_HAS_CANONICAL = False
try:
    from src.canonical_domain import resolve_canonical_domain
    _HAS_CANONICAL = True
except ImportError:
    pass

# Import dynamic reputation - gracefully handles missing module
_HAS_DYNAMIC_REP = False
try:
    from src.dynamic_reputation import compute_dynamic_reputation
    _HAS_DYNAMIC_REP = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# EXPANDED PUBLISHER REPUTATION SCORES (0-100)
# ---------------------------------------------------------------------------
# Categories:
#   95-100  : Highly Trusted (major international wire services & broadcasters)
#   85-94   : Very Trustworthy (major established newspapers & broadcasters)
#   75-84   : Trustworthy (quality outlets, established regional broadcasters)
#   60-74   : Mixed Reliability (tabloids, opinion-heavy outlets)
#   40-59   : Low Reliability (clickbait, conspiracy, state propaganda)
#   0-39    : Very Low Reliability (known disinformation sources)
# ---------------------------------------------------------------------------

SOURCE_SCORES = {
    # ===== FACTUAL / VERIFIED =====
    "reuters.com": 98,
    "apnews.com": 97,
    "ap.org": 97,
    "bbc.com": 95,
    "bbc.co.uk": 95,

    # ===== VERY TRUSTWORTHY =====
    "afp.com": 95,
    "npr.org": 94,
    "theguardian.com": 92,
    "nytimes.com": 92,
    "washingtonpost.com": 91,
    "bloomberg.com": 90,
    "wsj.com": 90,
    "ft.com": 90,
    "aljazeera.com": 90,
    "economist.com": 93,
    "dw.com": 92,
    "france24.com": 90,
    "pbs.org": 92,

    # ===== TRUSTWORTHY =====
    "cnn.com": 88,
    "abcnews.go.com": 88,
    "cbsnews.com": 87,
    "nbcnews.com": 87,
    "forbes.com": 85,
    "usatoday.com": 84,
    "politico.com": 85,
    "thehill.com": 83,
    "newsweek.com": 80,
    "foxnews.com": 80,
    "latimes.com": 86,
    "chicagotribune.com": 84,

    # ===== INTERNATIONAL & REGIONAL =====
    "lemonde.fr": 88,
    "theguardian.com": 92,
    "independent.co.uk": 82,
    "telegraph.co.uk": 85,
    "thetimes.co.uk": 88,
    "irishtimes.com": 85,
    "smh.com.au": 84,
    "theage.com.au": 84,
    "scmp.com": 82,
    "japantimes.co.jp": 84,
    "straitstimes.com": 82,
    "timesofindia.indiatimes.com": 78,
    "hindu.com": 82,
    "al-monitor.com": 84,
    "middleeasteye.net": 80,
    "dailysabah.com": 75,

    # ===== AFRICAN NEWS ORGANIZATIONS =====
    "nation.africa": 80,
    "africanews.com": 82,
    "mg.co.za": 82,
    "news24.com": 80,
    "citizen.co.za": 75,
    "theeastafrican.co.ke": 78,
    "businessdailyafrica.com": 76,
    "observer.ug": 76,
    "guardian.ng": 78,
    "premiumtimesng.com": 78,
    "allafrica.com": 80,
    "ethiopiaobserver.com": 72,

    # ===== REGIONAL BROADCASTERS =====
    "abc.net.au": 88,
    "cbc.ca": 88,
    "cbcnews.ca": 87,
    "channel4.com": 86,
    "itv.com": 84,
    "skynews.com": 84,
    "euronews.com": 84,
    "zeenews.india.com": 74,
    "ndtv.com": 80,
    "al-arabiya.net": 78,
    "haaretz.com": 82,
    "ynetnews.com": 78,
    "timesofisrael.com": 80,
    "jpost.com": 78,

    # ===== MIXED RELIABILITY =====
    "dailymail.co.uk": 65,
    "the-sun.com": 60,
    "nypost.com": 65,
    "bostonherald.com": 68,
    "washingtontimes.com": 65,
    "spectator.co.uk": 72,
    "spectator.us": 70,
    "nationalreview.com": 70,
    "weeklystandard.com": 70,
    "theatlantic.com": 86,
    "newyorker.com": 88,
    "slate.com": 78,
    "vox.com": 76,
    "buzzfeednews.com": 70,
    "huffpost.com": 68,

    # ===== SOCIAL MEDIA =====
    "facebook.com": 40,
    "instagram.com": 40,
    "x.com": 40,
    "twitter.com": 40,
    "tiktok.com": 35,
    "threads.net": 40,
    "linkedin.com": 45,

    # ===== VIDEO =====
    "youtube.com": 50,
    "youtu.be": 50,
}

# ---------------------------------------------------------------------------
# LABEL THRESHOLDS
# ---------------------------------------------------------------------------

LABEL_THRESHOLDS = [
    (90, "Highly Trusted"),
    (75, "Trusted"),
    (60, "Mixed Reliability"),
    (0,  "Low Reliability"),
]


def get_domain(url):
    """
    Extract domain from URL.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        domain = domain.replace("www.", "")
        return domain
    except:
        return None


def get_source_rating(url, use_canonical=True, use_dynamic=False):
    """
    Return source reputation score with optional canonical domain resolution
    and dynamic reputation signals.

    Args:
        url: The article URL.
        use_canonical: If True (default), resolve shortened URLs, redirects,
                       mobile subdomains, and regional variants to their
                       parent publisher domain before scoring.
        use_dynamic: If True, compute dynamic reputation signals and
                     adjust the score accordingly (requires domain age
                     data, WHOIS, etc.). Default False.

    Returns:
        dict with domain, score, label, canonical resolution info.
    """
    raw_domain = get_domain(url)
    if not raw_domain:
        return {
            "domain": "Unknown",
            "score": 0,
            "label": "Unknown",
            "canonical": None,
            "resolution_method": "parse_failed",
        }

    canonical_info = {"original": raw_domain, "canonical": raw_domain, "resolution_method": "not_applied"}

    # Resolve to canonical domain
    if use_canonical and _HAS_CANONICAL:
        try:
            canonical_info = resolve_canonical_domain(url)
        except Exception:
            canonical_info = {"original": raw_domain, "canonical": raw_domain, "resolution_method": "error"}

    scoring_domain = canonical_info.get("canonical", raw_domain) or raw_domain

    # Look up base score
    base_score = SOURCE_SCORES.get(scoring_domain, 50)

    # Apply dynamic reputation adjustments
    dynamic_info = {}
    if use_dynamic and _HAS_DYNAMIC_REP:
        try:
            dynamic_result = compute_dynamic_reputation(url, scoring_domain)
            if dynamic_result:
                base_score = dynamic_result.get("adjusted_score", base_score)
                dynamic_info = dynamic_result.get("signals", {})
        except Exception:
            pass

    # Clamp score
    base_score = max(0, min(100, base_score))

    # Determine label
    label = "Unknown"
    for threshold, lbl in LABEL_THRESHOLDS:
        if base_score >= threshold:
            label = lbl
            break

    result = {
        "domain": scoring_domain,
        "score": base_score,
        "label": label,
        "canonical": canonical_info.get("canonical"),
        "original_domain": raw_domain,
        "resolution_method": canonical_info.get("resolution_method", "not_applied"),
    }

    if dynamic_info:
        result["dynamic"] = dynamic_info

    return result
