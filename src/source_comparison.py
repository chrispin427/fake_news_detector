from difflib import SequenceMatcher
import re


_COMMON_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "because", "but", "and", "or", "if", "while", "that", "this",
    "these", "those", "it", "its", "he", "she", "they", "them", "we", "you",
    "who", "which", "what", "new", "after", "says", "said", "also",
})


def _get_key_tokens(text):
    """
    Extract meaningful tokens (words that are not common English words).
    """
    text = text.lower()
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text)
    return {t for t in tokens if len(t) > 2 and t not in _COMMON_WORDS}


def _keyword_jaccard(tokens_a, tokens_b):
    """Jaccard similarity on keyword token sets."""
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return len(intersection) / len(union)


def _sequence_matcher_score(text_a, text_b):
    """Legacy string similarity as an auxiliary signal."""
    return SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()


def compare_sources(claim, evidence_articles):
    """
    Compare a detected claim against evidence article titles
    using a hybrid approach: keyword overlap (70%) + string similarity (30%).

    This prevents different-wording-same-event from being unfairly penalized.

    Returns dict with agreement (int), classification (str),
    sources_checked (int), and debug info.
    """
    if not evidence_articles or not claim:
        return {
            "agreement": 0,
            "classification": "Low Agreement",
            "sources_checked": 0,
            "debug": {
                "method": "N/A",
                "inputs": {"claim": str(claim)[:200], "num_evidence": len(evidence_articles) if evidence_articles else 0},
                "individual_scores": [],
                "avg_keyword_similarity": 0.0,
                "avg_string_similarity": 0.0,
                "final_calculation": "No input data"
            }
        }

    claim_tokens = _get_key_tokens(claim)
    claim_lower = claim.lower()

    keyword_scores = []
    string_scores = []
    individual = []

    for item in evidence_articles:
        title = item.get("title", "")
        if not title:
            continue

        title_tokens = _get_key_tokens(title)
        kw_sim = _keyword_jaccard(claim_tokens, title_tokens)
        keyword_scores.append(kw_sim)

        str_sim = _sequence_matcher_score(claim_lower, title.lower())
        string_scores.append(str_sim)

        individual.append({
            "evidence_title": title[:120],
            "keyword_similarity": round(kw_sim * 100, 2),
            "string_similarity": round(str_sim * 100, 2),
        })

    if not keyword_scores:
        return {
            "agreement": 0,
            "classification": "Low Agreement",
            "sources_checked": 0,
            "debug": {
                "method": "N/A",
                "inputs": {"claim": claim[:200], "num_evidence": len(evidence_articles)},
                "individual_scores": [],
                "avg_keyword_similarity": 0.0,
                "avg_string_similarity": 0.0,
                "final_calculation": "No valid evidence titles"
            }
        }

    # Weighted hybrid: 70% keyword overlap + 30% string similarity
    avg_keyword = sum(keyword_scores) / len(keyword_scores)
    avg_string = sum(string_scores) / len(string_scores)
    hybrid = (avg_keyword * 0.70) + (avg_string * 0.30)
    agreement = round(hybrid * 100)

    if agreement >= 70:
        classification = "High Agreement"
    elif agreement >= 40:
        classification = "Moderate Agreement"
    else:
        classification = "Low Agreement"

    # Debug logging
    calc = (
        f"keyword_jaccard={round(avg_keyword*100,1)}% * 0.70 + "
        f"string_similarity={round(avg_string*100,1)}% * 0.30 = "
        f"{round(hybrid*100,1)}% -> agreement={agreement}%"
    )
    print(f"\n--- SOURCE COMPARISON DEBUG ---")
    print(f"  Claim (tokens={len(claim_tokens)}): {claim[:120]}")
    print(f"  Evidence articles:         {len(evidence_articles)}")
    print(f"  Avg keyword similarity:    {round(avg_keyword*100, 2)}%")
    print(f"  Avg string similarity:     {round(avg_string*100, 2)}%")
    print(f"  Hybrid score:              {round(hybrid*100, 2)}%")
    print(f"  Final agreement:           {agreement}%")
    print(f"  Classification:            {classification}")
    print(f"  Calculation:               {calc}")
    print("-------------------------------\n")

    return {
        "agreement": agreement,
        "classification": classification,
        "sources_checked": len(evidence_articles),
        "debug": {
            "method": "hybrid (70% keyword_jaccard + 30% string_similarity)",
            "inputs": {
                "claim": claim[:200],
                "num_evidence": len(evidence_articles),
            },
            "individual_scores": individual,
            "avg_keyword_similarity": round(avg_keyword * 100, 2),
            "avg_string_similarity": round(avg_string * 100, 2),
            "hybrid_score": round(hybrid * 100, 2),
            "final_calculation": calc
        }
    }
