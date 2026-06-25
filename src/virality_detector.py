def calculate_virality(results_dict):

    total_mentions = sum(
        results_dict.values()
    )

    if total_mentions >= 50:

        level = "Very High"

    elif total_mentions >= 20:

        level = "High"

    elif total_mentions >= 5:

        level = "Moderate"

    else:

        level = "Low"

    return {
        "mentions": total_mentions,
        "level": level
    }