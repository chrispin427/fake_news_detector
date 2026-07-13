"""
src/canonical_domain.py

Canonical domain resolution module.
"""

from urllib.parse import urlparse

CANONICAL_MAP = {
    "aje.news": "aljazeera.com",
    "aje.io": "aljazeera.com",
    "aljazeera.net": "aljazeera.com",
    "m.aljazeera.com": "aljazeera.com",
    "amp.aljazeera.com": "aljazeera.com",
    "channels.aljazeera.com": "aljazeera.com",
    "bbc.in": "bbc.co.uk",
    "bbcnews.com": "bbc.com",
    "m.bbc.com": "bbc.com",
    "m.bbc.co.uk": "bbc.co.uk",
    "reut.rs": "reuters.com",
    "mobile.reuters.com": "reuters.com",
    "uk.reuters.com": "reuters.com",
    "in.reuters.com": "reuters.com",
    "fr.reuters.com": "reuters.com",
    "de.reuters.com": "reuters.com",
    "es.reuters.com": "reuters.com",
    "apne.ws": "apnews.com",
    "ap.org": "apnews.com",
    "bigstory.ap.org": "apnews.com",
    "nyti.ms": "nytimes.com",
    "mobile.nytimes.com": "nytimes.com",
    "wapo.st": "washingtonpost.com",
    "gu.com": "theguardian.com",
    "guardian.co.uk": "theguardian.com",
    "m.theguardian.com": "theguardian.com",
    "amp.theguardian.com": "theguardian.com",
    "bloom.bg": "bloomberg.com",
    "mobile.bloomberg.com": "bloomberg.com",
    "on.ft.com": "ft.com",
    "on.wsj.com": "wsj.com",
    "mobile.wsj.com": "wsj.com",
    "cnn.it": "cnn.com",
    "edition.cnn.com": "cnn.com",
    "n.pr": "npr.org",
    "nbcnews.to": "nbcnews.com",
    "abcn.ws": "abcnews.go.com",
    "fxn.ws": "foxnews.com",
    "usatoday.com": "usatoday.com",
    "eu.usatoday.com": "usatoday.com",
    "dw.com": "dw.com",
    "p.dw.com": "dw.com",
    "france24.com": "france24.com",
    "observers.france24.com": "france24.com",
    "youtu.be": "youtube.com",
    "fb.com": "facebook.com",
    "fb.watch": "facebook.com",
    "t.co": "twitter.com",
    "instagr.am": "instagram.com",
    "lnkd.in": "linkedin.com",
    "vm.tiktok.com": "tiktok.com",
}

THIRD_PARTY_PREFIXES = ["news.google.com", "apple.news", "flipboard.com", "news.yahoo.com"]


def get_domain_from_url(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return domain.replace("www.", "", 1) if domain.startswith("www.") else domain
    except Exception:
        return None


def resolve_canonical_domain(url_or_domain):
    is_url_input = url_or_domain.startswith("http://") or url_or_domain.startswith("https://")
    original_domain = get_domain_from_url(url_or_domain) if is_url_input else url_or_domain.lower().strip()
    if not original_domain:
        return {"original": url_or_domain, "canonical": None, "is_third_party": False, "resolution_method": "parse_failed"}
    original_domain = original_domain.replace("www.", "", 1) if original_domain.startswith("www.") else original_domain
    for prefix in THIRD_PARTY_PREFIXES:
        if original_domain == prefix:
            return {"original": original_domain, "canonical": original_domain, "is_third_party": True, "resolution_method": "third_party_aggregator"}
    if original_domain in CANONICAL_MAP:
        resolved = CANONICAL_MAP[original_domain]
        is_sub = original_domain != resolved
        return {"original": original_domain, "canonical": resolved, "is_third_party": False, "resolution_method": "canonical_map" if is_sub else "exact_match"}
    parts = original_domain.split(".")
    if len(parts) >= 3:
        for i in range(1, len(parts) - 1):
            candidate = ".".join(parts[i:])
            if candidate in CANONICAL_MAP:
                return {"original": original_domain, "canonical": CANONICAL_MAP[candidate], "is_third_party": False, "resolution_method": f"subdomain_strip"}
    for prefix in ["m.", "mobile.", "amp.", "i.", "text."]:
        if original_domain.startswith(prefix):
            stripped = original_domain[len(prefix):]
            if stripped in CANONICAL_MAP:
                return {"original": original_domain, "canonical": CANONICAL_MAP[stripped], "is_third_party": False, "resolution_method": f"prefix_strip"}
    return {"original": original_domain, "canonical": original_domain, "is_third_party": False, "resolution_method": "no_resolution"}
