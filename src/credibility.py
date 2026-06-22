def calculate_credibility_score(
    prediction,
    confidence,
    matched_sources,
    total_sources
):
    score = 0

    # ML confidence contributes up to 70 points
    score += confidence * 70

    # Source verification contributes up to 30 points
    if total_sources > 0:
        score += (matched_sources / total_sources) * 30

    # Penalize fake predictions
    if prediction == 0:
        score *= 0.6

    score = round(score)

    score = max(0, min(100, score))

    return score