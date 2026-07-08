import logging

# ------------------------------------------------------------------
# Logging setup for debug output
# ------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verdict_engine")


# ------------------------------------------------------------------
# Trusted publishers list (highly reputable sources)
# ------------------------------------------------------------------
TRUSTED_PUBLISHERS = [
    "reuters.com", "apnews.com", "ap.org", "bbc.com", "bbc.co.uk",
    "nbcnews.com", "abcnews.go.com", "cbsnews.com",
    "aljazeera.com", "ft.com", "bloomberg.com", "wsj.com",
    "npr.org", "theguardian.com", "nytimes.com", "washingtonpost.com"
]


# ------------------------------------------------------------------
# Weights (must sum to 100)
# ------------------------------------------------------------------
WEIGHTS = {
    "source_reputation": 35,
    "external_evidence": 25,
    "fact_check": 15,
    "timeline": 10,
    "manipulation": 5,
    "headline": 5,
    "ml_prediction": 5
}


def _score_source_reputation(source_info):
    """Score based on source reputation. Uses source score (0-100)."""
    score = source_info.get("score", 0) if source_info else 0
    weighted = score * (WEIGHTS["source_reputation"] / 100.0)
    return round(weighted, 2), score


def _score_external_evidence(evidence):
    """Score based on number of supporting evidence articles. 0 = 0%, 10+ = 100%."""
    num_articles = len(evidence) if evidence else 0
    pct = min(num_articles / 10.0, 1.0) * 100
    weighted = pct * (WEIGHTS["external_evidence"] / 100.0)
    return round(weighted, 2), round(pct, 1), num_articles


def _score_fact_check(fact_result, matched_sources, total_sources):
    """Score based on fact check verdict and matched sources ratio."""
    verdict = fact_result.get("verdict", "Unverified") if fact_result else "Unverified"
    if verdict == "Supported":
        pct = 100
    elif verdict == "Partially Supported":
        pct = 60
    elif matched_sources > 0 and total_sources > 0:
        pct = (matched_sources / total_sources) * 100
    else:
        pct = 15
    weighted = pct * (WEIGHTS["fact_check"] / 100.0)
    return round(weighted, 2), round(pct, 1), verdict


def _score_timeline(timeline_result):
    """Score based on timeline. Recent=100%, Not Recent=70%, Unknown=100% (neutral), Old=30%."""
    status = timeline_result.get("status", "Unknown") if timeline_result else "Unknown"
    if status == "Recent":
        pct = 100
    elif status == "Not Recent":
        pct = 70
    elif status == "Unknown":
        pct = 100  # Neutral — no penalty for missing information
    else:
        pct = 30  # Old Article
    weighted = pct * (WEIGHTS["timeline"] / 100.0)
    return round(weighted, 2), pct, status


def _score_manipulation(rewrite_result):
    """Score based on manipulation risk. Low=100%, Medium=50%, High=0%, Unknown=100% (neutral)."""
    risk = rewrite_result.get("risk", "Unknown") if rewrite_result else "Unknown"
    if risk == "Low":
        pct = 100
    elif risk == "Medium":
        pct = 50
    elif risk == "Unknown":
        pct = 100  # Neutral — no evidence to assess manipulation
    else:
        pct = 0  # High risk
    weighted = pct * (WEIGHTS["manipulation"] / 100.0)
    return round(weighted, 2), pct, risk


def _score_headline(headline_result):
    """Score based on headline risk. Low=100%, Medium=50%, High=0%."""
    risk = headline_result.get("risk", "Low") if headline_result else "Low"
    if risk == "Low":
        pct = 100
    elif risk == "Medium":
        pct = 50
    else:
        pct = 0
    weighted = pct * (WEIGHTS["headline"] / 100.0)
    return round(weighted, 2), pct, risk


def _score_ml_prediction(prediction, confidence):
    """Score based on ML prediction (supporting signal, 5% weight)."""
    if prediction == 1:
        pct = confidence * 100
    else:
        pct = (1.0 - confidence) * 40
    weighted = pct * (WEIGHTS["ml_prediction"] / 100.0)
    return round(weighted, 2), round(pct, 1), prediction, round(confidence, 4)


def _is_trusted_source(source_info):
    """Check if the source is a highly trusted publisher (score >= 90)."""
    if not source_info:
        return False
    domain = source_info.get("domain", "").lower()
    score = source_info.get("score", 0)
    return domain in TRUSTED_PUBLISHERS and score >= 90


def _check_fake_conditions(source_info, evidence, rewrite_result, headline_result,
                           source_comparison_result, prediction, confidence):
    """
    Fake verdict safeguards: require at least 2 negative conditions
    before allowing a Suspicious or Highly Suspicious verdict.
    """
    conditions = []
    reasons = []
    source_score = source_info.get("score", 0) if source_info else 0
    if source_score < 60:
        conditions.append("low_source")
        reasons.append("Low source reputation")
    num_evidence = len(evidence) if evidence else 0
    if num_evidence < 3:
        conditions.append("weak_evidence")
        reasons.append("Fewer than 3 supporting articles found")
    manip_risk = rewrite_result.get("risk", "High") if rewrite_result else "High"
    if manip_risk == "High":
        conditions.append("manipulation_detected")
        reasons.append("Content manipulation detected")
    # Unknown manipulation risk is NOT counted as a negative condition
    agreement = source_comparison_result.get("agreement", 0) if source_comparison_result else 0
    if agreement < 40:
        conditions.append("low_agreement")
        reasons.append("Low agreement with trusted sources")
    headline_risk = headline_result.get("risk", "Low") if headline_result else "Low"
    if headline_risk == "High":
        conditions.append("misleading_headline")
        reasons.append("Headline shows clickbait or sensationalism patterns")
    if confidence < 0.6:
        conditions.append("low_ml_confidence")
        reasons.append("Low ML model confidence")
    return conditions, reasons


def _count_strong_negative_signals(rewrite_result, headline_result, fact_result, confidence):
    """
    Count truly independent negative signals that justify overriding
    a trusted-source presumption of credibility.

    Signals counted:
    - Manipulation: rewrite risk is High
    - Clickbait: headline risk is High
    - Failed fact check: verdict is Unverified with 0 matched sources
    - Very low ML confidence: confidence < 0.6

    Returns:
        Tuple of (count, list of signal names)
    """
    signals = []

    # Manipulation signal
    manip_risk = rewrite_result.get("risk", "Low") if rewrite_result else "Low"
    if manip_risk == "High":
        signals.append("manipulation")

    # Clickbait / sensational headline signal
    hl_risk = headline_result.get("risk", "Low") if headline_result else "Low"
    if hl_risk == "High":
        signals.append("clickbait")

    # Failed fact check signal
    fc_verdict = fact_result.get("verdict", "Unverified") if fact_result else "Unverified"
    fc_sources = fact_result.get("sources", 0) if fact_result else 0
    if fc_verdict == "Unverified" and fc_sources == 0:
        signals.append("failed_fact_check")

    # Very low ML confidence signal
    if confidence is not None and confidence < 0.6:
        signals.append("low_confidence")

    return len(signals), signals


def _determine_verdict(score, conditions_met, conditions_reasons, is_trusted,
                       source_info, evidence, source_comparison_result,
                       rewrite_result=None, headline_result=None,
                       fact_result=None, confidence=None):
    """
    Determine final verdict category based on score and context.
    Applies trusted source overrides and evidence-based verification.

    Strengthened override logic:
    - Sources with reputation 90+ (BBC, Reuters, AP, etc.) get a strong
      presumption of credibility. Weak evidence alone does not reduce
      the verdict below "Likely Credible" unless there are multiple
      independent negative signals (manipulation, clickbait, failed
      fact checking, or very low ML confidence).
    """
    explanations = []
    final_score = score
    source_score = source_info.get("score", 0) if source_info else 0
    num_evidence = len(evidence) if evidence else 0
    agreement = source_comparison_result.get("agreement", 0) if source_comparison_result else 0

    # --- Debug logging ---
    logger.info("")
    logger.info("-" * 50)
    logger.info("DETERMINE VERDICT - DEBUG")
    logger.info("-" * 50)
    logger.info("Initial score:          %s", score)
    logger.info("Trusted source:         %s (domain=%s, score=%s)", is_trusted,
                source_info.get("domain", "N/A") if source_info else "N/A", source_score)
    logger.info("Evidence count:         %s", num_evidence)
    logger.info("Agreement:              %s%%", agreement)
    logger.info("Conditions met:         %s", conditions_met)
    logger.info("Condition reasons:      %s", conditions_reasons)

    # Count strong negative signals for trusted source override
    strong_count, strong_signals = _count_strong_negative_signals(
        rewrite_result, headline_result, fact_result, confidence
    )
    logger.info("Strong negative signals: %s (count=%s)", strong_signals, strong_count)

    # --- Trusted Source Override (strengthened) ---
    if is_trusted:
        explanations.append("Published by a highly trusted news source")

        # When source score >= 90, apply strong presumption of credibility
        if source_score >= 90:
            # Only allow score reduction below Likely Credible (75) if there
            # are at least 2 independent negative signals
            if final_score < 75 and strong_count < 2:
                old_score = final_score
                final_score = 75
                logger.info("TRUSTED-SOURCE OVERRIDE: score raised from %s to 75 (strong negatives=%s, need >=2)",
                            old_score, strong_count)
                explanations.append(
                    "Trusted-source override: preserved Likely Credible despite limited evidence"
                )
            elif final_score >= 75:
                # Still add positive reinforcement if score is already good
                if num_evidence >= 3:
                    explanations.append(
                        "Trusted source with " + str(num_evidence) + " supporting articles - credibility reinforced"
                    )
                if agreement >= 70:
                    explanations.append(
                        "Strong agreement with trusted sources - leaning credible"
                    )

        # Fallback override for trusted sources with < 2 conditions met
        if len(conditions_met) < 2 and final_score < 50:
            old_score = final_score
            final_score = 55
            logger.info("TRUSTED-SOURCE OVERRIDE (fallback): score raised from %s to 55", old_score)
            explanations.append("Trusted source override: insufficient evidence for suspicious verdict")

    # --- Evidence-Based Verification ---
    if source_score >= 85 and num_evidence >= 3:
        explanations.append("Published by trusted source")
        explanations.append("Supported by " + str(num_evidence) + " external articles")

    if num_evidence == 0:
        explanations.append("No supporting evidence found")

    for reason in conditions_reasons:
        if reason not in explanations:
            explanations.append(reason)

    final_score = max(0, min(100, final_score))

    # --- Verdict categories ---
    if final_score >= 90:
        verdict = "Highly Credible"
        if not any("trusted source" in e.lower() for e in explanations):
            explanations.insert(0, "Strong across all verification signals")
    elif final_score >= 75:
        verdict = "Likely Credible"
    elif final_score >= 50:
        verdict = "Mixed Evidence"
    elif final_score >= 30:
        verdict = "Suspicious"
    else:
        verdict = "Highly Suspicious"

    # Contextual explanations for suspicious verdicts
    if verdict in ("Suspicious", "Highly Suspicious"):
        if "No supporting evidence found" not in explanations:
            explanations.append("Weak source reputation")
        if not any("manipulation" in e.lower() for e in explanations):
            explanations.append("Multiple signals indicate potential misinformation")

    # Deduplicate explanations while preserving order
    seen = set()
    unique_explanations = []
    for e in explanations:
        if e not in seen:
            seen.add(e)
            unique_explanations.append(e)

    logger.info("FINAL VERDICT: %s (score=%s)", verdict, final_score)
    logger.info("EXPLANATIONS: %s", unique_explanations)
    logger.info("-" * 50)

    return verdict, unique_explanations, final_score


def generate_verdict(
    source_info=None,
    prediction=None,
    confidence=0.5,
    credibility_score=50,
    matched_sources=0,
    total_sources=0,
    fact_result=None,
    evidence=None,
    sentiment_result=None,
    risk_result=None,
    timeline_result=None,
    headline_result=None,
    rewrite_result=None,
    source_comparison_result=None
):
    """
    Combines all detector outputs into one final verdict using a
    weighted, multi-signal decision system.

    The ML prediction is a supporting signal (5% weight), not the
    primary decision driver.

    Returns dict with score, verdict, explanations, breakdown, conditions_met, is_trusted_source.
    """
    # Default fallbacks
    if source_info is None:
        source_info = {"domain": "Unknown", "score": 50, "label": "Unknown"}
    if fact_result is None:
        fact_result = {"verdict": "Unverified", "sources": 0, "results": {}}
    if evidence is None:
        evidence = []
    if sentiment_result is None:
        sentiment_result = {"polarity": 0, "sensational_words": [], "manipulation_risk": "Low"}
    if risk_result is None:
        risk_result = {"risk_categories": ["General"], "high_risk": False, "risk_level": "Low"}
    if timeline_result is None:
        timeline_result = {"status": "Unknown", "years_old": None, "is_old_news": False}
    if headline_result is None:
        headline_result = {"headline": "", "risk": "Low", "score": 0, "reasons": []}
    if rewrite_result is None:
        rewrite_result = {"similarity": 0.0, "risk": "Unknown", "explanation": "No evidence available for comparison"}
    if source_comparison_result is None:
        source_comparison_result = {"agreement": 0, "classification": "Low Agreement", "sources_checked": 0}

    # Score each signal
    src_score, src_raw = _score_source_reputation(source_info)
    evid_score, evid_pct, evid_count = _score_external_evidence(evidence)
    fc_score, fc_pct, fc_verdict = _score_fact_check(fact_result, matched_sources, total_sources)
    tl_score, tl_pct, tl_status = _score_timeline(timeline_result)
    manip_score, manip_pct, manip_risk = _score_manipulation(rewrite_result)
    hl_score, hl_pct, hl_risk = _score_headline(headline_result)
    ml_score, ml_pct, ml_prediction, ml_conf = _score_ml_prediction(prediction, confidence)

    # Compute final weighted score
    total = round(src_score + evid_score + fc_score + tl_score + manip_score + hl_score + ml_score, 2)

    # Build score breakdown
    breakdown = {
        "source_reputation": {"weight": WEIGHTS["source_reputation"], "raw": src_raw, "weighted": src_score},
        "external_evidence": {"weight": WEIGHTS["external_evidence"], "raw": evid_pct, "weighted": evid_score, "articles": evid_count},
        "fact_check": {"weight": WEIGHTS["fact_check"], "raw": fc_pct, "weighted": fc_score, "verdict": fc_verdict},
        "timeline": {"weight": WEIGHTS["timeline"], "raw": tl_pct, "weighted": tl_score, "status": tl_status},
        "manipulation": {"weight": WEIGHTS["manipulation"], "raw": manip_pct, "weighted": manip_score, "risk": manip_risk},
        "headline": {"weight": WEIGHTS["headline"], "raw": hl_pct, "weighted": hl_score, "risk": hl_risk},
        "ml_prediction": {"weight": WEIGHTS["ml_prediction"], "raw": ml_pct, "weighted": ml_score, "prediction": ml_prediction, "confidence": ml_conf}
    }

    # Logging for debugging/tuning
    logger.info("=" * 50)
    logger.info("VERDICT ENGINE SCORES")
    logger.info("=" * 50)
    logger.info("Source Score:           %s (raw=%s, weight=%s%%)", src_score, src_raw, WEIGHTS["source_reputation"])
    logger.info("Evidence Score:         %s (raw=%s%%, articles=%s, weight=%s%%)", evid_score, evid_pct, evid_count, WEIGHTS["external_evidence"])
    logger.info("Fact Check Score:       %s (raw=%s%%, verdict=%s, weight=%s%%)", fc_score, fc_pct, fc_verdict, WEIGHTS["fact_check"])
    logger.info("Timeline Score:         %s (raw=%s%%, status=%s, weight=%s%%)", tl_score, tl_pct, tl_status, WEIGHTS["timeline"])
    logger.info("Manipulation Score:     %s (raw=%s%%, risk=%s, weight=%s%%)", manip_score, manip_pct, manip_risk, WEIGHTS["manipulation"])
    logger.info("Headline Score:         %s (raw=%s%%, risk=%s, weight=%s%%)", hl_score, hl_pct, hl_risk, WEIGHTS["headline"])
    logger.info("ML Prediction Score:    %s (raw=%s%%, pred=%s, conf=%s, weight=%s%%)", ml_score, ml_pct, ml_prediction, ml_conf, WEIGHTS["ml_prediction"])
    logger.info("-" * 50)
    logger.info("FINAL WEIGHTED SCORE:   %s", total)
    logger.info("-" * 50)

    # Check trusted source
    is_trusted = _is_trusted_source(source_info)

    # Check fake verdict conditions
    conditions_met, condition_reasons = _check_fake_conditions(
        source_info, evidence, rewrite_result, headline_result,
        source_comparison_result, prediction, confidence
    )

    # Determine verdict with overrides (pass additional params for strengthened override)
    verdict, explanations, final_score = _determine_verdict(
        total, conditions_met, condition_reasons, is_trusted,
        source_info, evidence, source_comparison_result,
        rewrite_result=rewrite_result, headline_result=headline_result,
        fact_result=fact_result, confidence=confidence
    )

    logger.info("SOURCE: %s (score=%s, trusted=%s)", source_info.get("domain", "N/A"), source_info.get("score", 0), is_trusted)
    logger.info("CONDITIONS MET: %s", len(conditions_met))
    logger.info("REWRITE SIMILARITY: %s, RISK: %s", rewrite_result.get("similarity", "N/A"), rewrite_result.get("risk", "N/A"))
    logger.info("EVIDENCE COUNT: %s", len(evidence) if evidence else 0)
    logger.info("AGREEMENT: %s%%", source_comparison_result.get("agreement", 0) if source_comparison_result else "N/A")
    logger.info("FINAL VERDICT: %s (score=%s)", verdict, final_score)
    logger.info("EXPLANATIONS: %s", explanations)

    return {
        "score": final_score,
        "verdict": verdict,
        "explanations": explanations,
        "breakdown": breakdown,
        "conditions_met": conditions_met,
        "is_trusted_source": is_trusted
    }