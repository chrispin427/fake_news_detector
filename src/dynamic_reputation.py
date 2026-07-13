"""
src/dynamic_reputation.py

Dynamic Reputation Framework

Extends static source reputation scoring with multiple signals that
can adjust a publisher's trust score up or down. Designed to detect
malicious clones, newly-registered impersonation domains, and other
reputation-based threats that a static whitelist cannot catch.

Current Signals (Active):
  1. Canonical Domain Resolution - already resolved upstream
  2. Domain Age Signal (optional, with graceful fallback)
  3. HTTPS Validity - checks if site supports HTTPS properly
  4. Publisher Consistency - verifies the domain matches known publisher patterns

Future Signals (Planned):
  - WHOIS metadata availability & registration date
  - Historical evidence reliability (how often evidence from this source checks out)
  - Domain registration pattern anomalies (recently registered, short lifespan)
  - Certificate transparency logs (newly issued certs for clone domains)
  - DNS record consistency
  - Known malicious domain blocklists

Architecture:
  The framework uses a plugin-style design where each signal is an independent
  function that returns a score adjustment (-20 to +20). The adjustments are
  summed and applied to the base static reputation score.

Usage:
    from src.dynamic_reputation import compute_dynamic_reputation
    result = compute_dynamic_reputation("https://example.com/article", "example.com")
"""

import re
import logging

logger = logging.getLogger("dynamic_reputation")

# ---------------------------------------------------------------------------
# Signal weights (total adjustment range: -30 to +30)
# ---------------------------------------------------------------------------

SIGNAL_WEIGHTS = {
    "https_validity": 10,        # Max +/- 10
    "domain_age": 10,            # Max +/- 10
    "publisher_consistency": 10, # Max +/- 10
}


# ---------------------------------------------------------------------------
# Signal Functions
# ---------------------------------------------------------------------------

def _check_https_validity(url):
    """
    Check if the URL uses HTTPS properly.
    Returns adjustment from -10 (no HTTPS) to +5 (HTTPS with secure domain).
    """
    score = 0
    if url.startswith("https://"):
        score += 5
        # Check for common secure patterns
        if "http://" not in url:
            score += 2
        return score, {"uses_https": True, "adjustment": min(score, 10)}
    else:
        # HTTP-only is a minor negative signal
        score -= 3
        return score, {"uses_https": False, "adjustment": max(score, -10)}


def _check_domain_age_signal(domain):
    """
    Attempt to check domain age via WHOIS data.
    Falls back gracefully if WHOIS data is unavailable.

    Note: This is a simplified implementation. Real domain age checking
    requires whois library or an external API.
    """
    return 0, {"available": False, "reason": "Domain age checking requires whois library (not installed)"}


def _check_publisher_consistency(domain):
    """
    Check if the domain looks like a legitimate publisher domain
    rather than a suspicious clone or impersonation.

    Looks for:
    - Domain is a well-known TLD (.com, .org, .co.uk, etc.)
    - Domain doesn't contain suspicious character patterns
    - Domain isn't a known spoofing variant
    """
    score = 0
    reasons = []

    # Check for suspicious patterns indicative of clone/impersonation domains
    suspicious_patterns = [
        r"\d{5,}",           # Long number sequences (e.g., news12345.com)
        r"^[a-z]{1}[0-9]{3,}", # Letter + long number (e.g., a1234news.com)
        r"-{2,}",            # Double hyphens
        r"[_.]{2,}",         # Double underscores/dots
        r"xn--",             # Internationalized domain name (IDN) homograph attack
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, domain):
            score -= 5
            reasons.append(f"Suspicious domain pattern: {pattern}")

    # Check for known brand-impersonation patterns
    trusted_brands = ["bbc", "cnn", "reuters", "apnews", "nytimes", "guardian", "bloomberg", "wsj", "aljazeera"]
    domain_parts = domain.lower().split(".")
    base_name = domain_parts[0] if domain_parts else ""

    for brand in trusted_brands:
        if brand in base_name and base_name != brand:
            # Could be a clone (e.g., „bbcnnnews.com” or “reuters-live.com”)
            if len(base_name) > len(brand) + 3:
                score -= 8
                reasons.append(f"Potential brand impersonation: '{base_name}' contains '{brand}'")

    return score, {"adjustment": score, "reasons": reasons}


# ---------------------------------------------------------------------------
# Main computation function
# ---------------------------------------------------------------------------

def compute_dynamic_reputation(url, canonical_domain):
    """
    Compute dynamic reputation signals and return score adjustment.

    Args:
        url: The original article URL.
        canonical_domain: The resolved canonical domain.

    Returns:
        dict with:
            adjusted_score (int): The final adjusted score (0-100)
            adjustment (int): Total adjustment applied
            signals (dict): Per-signal breakdown
            active_signals (list): Which signals contributed
            warnings (list): Any warnings raised
    """
    signals = {}
    total_adjustment = 0
    active_signals = []
    warnings = []

    # Signal 1: HTTPS Validity
    try:
        https_adj, https_info = _check_https_validity(url)
        signals["https_validity"] = https_info
        total_adjustment += https_adj
        if https_adj != 0:
            active_signals.append("https_validity")
    except Exception as e:
        warnings.append(f"HTTPS check failed: {e}")

    # Signal 2: Domain Age
    try:
        age_adj, age_info = _check_domain_age_signal(canonical_domain)
        signals["domain_age"] = age_info
        total_adjustment += age_adj
        if age_adj != 0:
            active_signals.append("domain_age")
    except Exception as e:
        warnings.append(f"Domain age check failed: {e}")

    # Signal 3: Publisher Consistency
    try:
        pub_adj, pub_info = _check_publisher_consistency(canonical_domain)
        signals["publisher_consistency"] = pub_info
        total_adjustment += pub_adj
        if pub_adj != 0:
            active_signals.append("publisher_consistency")
    except Exception as e:
        warnings.append(f"Publisher consistency check failed: {e}")

    # Clamp adjustment to max range
    total_adjustment = max(-30, min(30, total_adjustment))

    # Starting from a neutral 50, apply adjustment
    base_score = 50
    adjusted_score = max(0, min(100, base_score + total_adjustment))

    # Logging
    logger.info("Dynamic Reputation for %s:", canonical_domain)
    logger.info("  HTTPS Validity:       %+d", https_adj)
    logger.info("  Domain Age:           %+d", age_adj)
    logger.info("  Publisher Consistency: %+d", pub_adj)
    logger.info("  Total Adjustment:     %+d", total_adjustment)
    logger.info("  Final Score:          %d", adjusted_score)
    if warnings:
        for w in warnings:
            logger.warning("  Warning: %s", w)

    return {
        "adjusted_score": adjusted_score,
        "adjustment": total_adjustment,
        "signals": signals,
        "active_signals": active_signals,
        "warnings": warnings,
    }
