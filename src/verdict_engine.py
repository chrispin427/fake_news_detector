def generate_verdict(
    prediction,
    confidence,
    credibility_score,
    matched_sources,
    total_sources,
    sentiment_result,
    risk_result,
    timeline_result,
    headline_result,
    rewrite_result,
    source_comparison_result
):
    """
    Combines all detector outputs into
    one final verdict.
    """

    score = 0

    # ----------------------------------
    # ML Model
    # ----------------------------------

    if prediction == 1:
        score += 30
    else:
        score -= 30

    # ----------------------------------
    # Confidence
    # ----------------------------------

    score += int(confidence * 20)

    # ----------------------------------
    # Credibility
    # ----------------------------------

    score += int(credibility_score / 5)

    # ----------------------------------
    # Source Matches
    # ----------------------------------

    if total_sources > 0:

        ratio = matched_sources / total_sources

        score += int(ratio * 20)

    # ----------------------------------
    # Sentiment
    # ----------------------------------

    if (
        sentiment_result["manipulation_risk"]
        == "High"
    ):
        score -= 15

    elif (
        sentiment_result["manipulation_risk"]
        == "Medium"
    ):
        score -= 8

    # ----------------------------------
    # Risk Detector
    # ----------------------------------

    if risk_result["risk_level"] == "High":
        score -= 10

    elif risk_result["risk_level"] == "Medium":
        score -= 5

    # ----------------------------------
    # Timeline
    # ----------------------------------

    if timeline_result["is_old_news"]:
        score -= 15

    # ----------------------------------
    # Headline
    # ----------------------------------

    if headline_result["risk"] == "High":
        score -= 15

    elif headline_result["risk"] == "Medium":
        score -= 8

    # ----------------------------------
    # Rewrite
    # ----------------------------------

    if (
        rewrite_result["risk"]
        == "Potential Manipulation"
    ):
        score -= 20

    # ----------------------------------
    # Source Comparison
    # ----------------------------------

    score += int(
        source_comparison_result["agreement"] / 10
    )

    # ----------------------------------
    # Clamp
    # ----------------------------------

    score = max(0, min(score, 100))

    # ----------------------------------
    # Verdict
    # ----------------------------------

    if score >= 80:

        verdict = "Highly Credible"

    elif score >= 60:

        verdict = "Likely Credible"

    elif score >= 40:

        verdict = "Uncertain"

    elif score >= 20:

        verdict = "Suspicious"

    else:

        verdict = "Likely Fake"

    return {
        "score": score,
        "verdict": verdict
    }