def generate_explanation(
    prediction,
    confidence,
    matched_sources,
    total_sources
):
    explanations = []

    # Prediction
    if prediction == 1:
        explanations.append(
            "The machine learning model classified this content as likely real news."
        )
    else:
        explanations.append(
            "The machine learning model classified this content as potentially fake or misleading."
        )

    # Confidence
    if confidence >= 0.90:
        explanations.append(
            "The model made this prediction with very high confidence."
        )
    elif confidence >= 0.75:
        explanations.append(
            "The model made this prediction with moderate confidence."
        )
    else:
        explanations.append(
            "The model has low confidence in this prediction."
        )

    # Source verification
    if matched_sources == total_sources:
        explanations.append(
            "The topic was found across all verification sources."
        )
    elif matched_sources > 0:
        explanations.append(
            f"The topic was found in {matched_sources} out of {total_sources} verification sources."
        )
    else:
        explanations.append(
            "No matching articles were found in external verification sources."
        )

    # Final recommendation
    if prediction == 0 or matched_sources == 0:
        explanations.append(
            "Additional fact-checking is recommended before trusting or sharing this content."
        )
    else:
        explanations.append(
            "The content appears credible based on both the AI model and source verification."
        )

    return explanations