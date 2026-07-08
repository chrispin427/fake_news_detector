"""
src/debug_audit.py

Diagnostic utility that generates a complete trace of an article's
journey through the detection pipeline.  Designed specifically to
help diagnose future false positives.

Usage:
    from src.debug_audit import audit_article
    trace = audit_article("https://www.bbc.com/news/articles/...")
    print(trace)

This module does NOT affect production behavior - it is purely
a debugging / forensics tool.
"""

import sys
import os

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.social_media import is_url
from src.url_extractor import extract_article
from src.source_rating import get_source_rating
from src.evidence_finder import find_evidence
from src.claim_extractor import extract_claim
from src.fact_checker import fact_check
from src.similarity_checker import calculate_similarity
from src.sentiment_analyzer import analyze_sentiment
from src.virality_detector import calculate_virality
from src.risk_detector import detect_risk
from src.timeline_checker import check_timeline
from src.source_comparison import compare_sources
from src.headline_checker import analyze_headline
from src.rewrite_detector import detect_rewrite
from src.verdict_engine import generate_verdict
from src.news_api import verify_news


def _normalise_source(src):
    """Handle source being a string, dict, or None."""
    if isinstance(src, dict):
        return src.get("name", str(src))
    if src is None:
        return "Unknown"
    return str(src)


def audit_article(input_text):
    """
    Run the full pipeline on input_text (URL or plain text)
    and return a structured dictionary with every intermediate
    signal, score, and decision.
    """
    trace = {
        "input": input_text[:500],
        "input_type": "URL" if is_url(input_text) else "TEXT",
    }

    trace["source"] = {"domain": "N/A", "score": 50, "label": "Unknown"}
    trace["article_title"] = "User-Submitted Text"
    trace["publish_date"] = None
    text_to_analyze = input_text

    if is_url(input_text):
        article = extract_article(input_text)
        trace["url_extraction"] = {
            "success": article.get("success", False),
            "source_type": article.get("source_type", "failed"),
            "error": article.get("error"),
        }
        if article.get("success", False):
            text_to_analyze = article.get("text", "")
            trace["article_title"] = article.get("title", "Untitled")
            raw_date = article.get("publish_date")
            trace["publish_date"] = str(raw_date) if raw_date else None
            trace["url_extraction"]["title"] = article.get("title", "")
            trace["url_extraction"]["authors"] = article.get("authors", [])
            trace["url_extraction"]["text_length"] = len(text_to_analyze)
        trace["source"] = get_source_rating(input_text)

    trace["word_count"] = len(text_to_analyze.split())

    claim_text = extract_claim(text_to_analyze)
    trace["claim"] = {"text": claim_text[:500], "length": len(claim_text)}

    evidence_query = trace["article_title"]
    if evidence_query in ("User-Submitted Text", "Untitled Article"):
        evidence_query = claim_text if claim_text else " ".join(text_to_analyze.split()[:10])

    evidence = find_evidence(evidence_query)
    trace["evidence"] = {
        "query": evidence_query[:200],
        "total_found": len(evidence),
        "articles": [
            {"source": _normalise_source(e.get("source", "?")), "title": e.get("title", "")[:120], "url": e.get("url", "")[:100]}
            for e in evidence[:10]
        ],
        "api_sources": _extract_api_sources(evidence),
    }

    sim_claim_article = calculate_similarity(claim_text, text_to_analyze) if claim_text else 0
    trace["similarity"] = {"claim_vs_article": sim_claim_article}

    source_comparison_result = compare_sources(claim_text, evidence)
    trace["source_agreement"] = source_comparison_result

    rewrite_result = detect_rewrite(claim_text, evidence)
    trace["rewrite"] = rewrite_result

    fact_result = fact_check(text_to_analyze)
    trace["fact_check"] = {
        "verdict": fact_result.get("verdict", "Unverified"),
        "sources_matched": fact_result.get("sources", 0),
        "results": fact_result.get("results", {}),
    }

    publish_date_parsed = None
    raw_date = trace.get("publish_date")
    if raw_date and raw_date != "None":
        try:
            from datetime import datetime
            publish_date_parsed = datetime.strptime(raw_date[:10], "%Y-%m-%d") if len(raw_date) >= 10 else None
        except (ValueError, TypeError):
            publish_date_parsed = None
    timeline_result = check_timeline(publish_date_parsed)
    trace["timeline"] = timeline_result

    sentiment_result = analyze_sentiment(text_to_analyze)
    trace["sentiment"] = sentiment_result

    results_dict, _ = verify_news(text_to_analyze)
    virality_result = calculate_virality(results_dict)
    trace["virality"] = virality_result

    risk_result = detect_risk(text_to_analyze)
    risk_level = "High" if risk_result.get("high_risk") else "Low"
    adapted_risk = {**risk_result, "risk_level": risk_level}
    trace["risk"] = adapted_risk

    headline_result = analyze_headline(trace["article_title"])
    trace["headline"] = headline_result

    try:
        from src.analyzer import analyze_article
        ml = analyze_article(text_to_analyze)
        trace["ml"] = {
            "prediction": int(ml["prediction"]),
            "label": "REAL" if ml["prediction"] == 1 else "FAKE",
            "confidence": round(ml["confidence"], 4),
            "probabilities": [round(p, 4) for p in ml["probabilities"]],
        }
    except Exception as e:
        trace["ml"] = {"error": str(e)}

    matched_sources = sum(1 for v in results_dict.values() if v > 0) if results_dict else 0
    total_sources = len(results_dict) if results_dict else 0
    adapted_timeline = {**timeline_result, "is_old_news": (timeline_result.get("status") == "Old Article")}

    verdict_result = generate_verdict(
        source_info=trace["source"],
        prediction=trace["ml"].get("prediction", 0),
        confidence=trace["ml"].get("confidence", 0.5),
        matched_sources=matched_sources,
        total_sources=total_sources if total_sources > 0 else 1,
        fact_result=fact_result,
        evidence=evidence,
        sentiment_result=sentiment_result,
        risk_result=adapted_risk,
        timeline_result=adapted_timeline,
        headline_result=headline_result,
        rewrite_result=rewrite_result,
        source_comparison_result=source_comparison_result,
    )
    trace["verdict"] = {
        "score": verdict_result.get("score", 0),
        "verdict": verdict_result.get("verdict", "N/A"),
        "explanations": verdict_result.get("explanations", []),
        "breakdown": verdict_result.get("breakdown", {}),
        "conditions_met": verdict_result.get("conditions_met", []),
        "is_trusted_source": verdict_result.get("is_trusted_source", False),
    }

    return trace


def _extract_api_sources(evidence):
    """Count evidence items by source, handling non-string source values."""
    from collections import Counter
    sources = Counter()
    for item in evidence:
        src = item.get("source", "")
        if isinstance(src, dict):
            src = src.get("name", str(src))
        if src is None:
            src = "Unknown"
        sources[str(src)] += 1
    return dict(sources.most_common(10))


def print_audit(trace):
    """Pretty-print the audit trace to stdout."""
    sep = "=" * 65
    print(f"\n{sep}")
    print("  AUDIT TRACE - Article Pipeline Diagnosis")
    print(f"{sep}")
    print(f"  Input:            {trace.get('input', '')[:100]}")
    print(f"  Type:             {trace.get('input_type', 'N/A')}")
    print(f"  Word count:       {trace.get('word_count', 0)}")

    s = trace.get("source", {})
    print(f"\n  1. SOURCE")
    print(f"     Domain:        {s.get('domain', 'N/A')}")
    print(f"     Score:         {s.get('score', 0)}/100")
    print(f"     Label:         {s.get('label', 'N/A')}")

    c = trace.get("claim", {})
    print(f"\n  2. CLAIM EXTRACTED")
    print(f"     Text:          {c.get('text', '')[:150]}")

    ev = trace.get("evidence", {})
    print(f"\n  3. EVIDENCE RETRIEVAL")
    print(f"     Query:         {ev.get('query', '')[:120]}")
    print(f"     Total found:   {ev.get('total_found', 0)}")
    for api, count in ev.get("api_sources", {}).items():
        print(f"       {api}: {count}")
    for i, art in enumerate(ev.get("articles", [])[:5], 1):
        print(f"     {i}. [{art.get('source', '?')}] {art.get('title', '')[:100]}")

    sim = trace.get("similarity", {})
    print(f"\n  4. SIMILARITY SCORES")
    print(f"     Claim vs article: {sim.get('claim_vs_article', 0)}%")

    ag = trace.get("source_agreement", {})
    print(f"\n  5. SOURCE AGREEMENT")
    print(f"     Agreement:      {ag.get('agreement', 0)}%")
    print(f"     Classification: {ag.get('classification', 'N/A')}")
    print(f"     Sources:        {ag.get('sources_checked', 0)}")

    rw = trace.get("rewrite", {})
    print(f"\n  6. REWRITE / MANIPULATION")
    print(f"     Similarity:     {rw.get('similarity', 0)}%")
    print(f"     Risk:           {rw.get('risk', 'N/A')}")
    print(f"     Explanation:    {rw.get('explanation', '')[:120]}")

    fc = trace.get("fact_check", {})
    print(f"\n  7. FACT CHECK")
    print(f"     Verdict:        {fc.get('verdict', 'N/A')}")
    print(f"     Sources:        {fc.get('sources_matched', 0)}")

    tl = trace.get("timeline", {})
    print(f"\n  8. TIMELINE")
    print(f"     Status:         {tl.get('status', 'N/A')}")
    print(f"     Years old:      {tl.get('years_old', 'N/A')}")

    ml = trace.get("ml", {})
    print(f"\n  9. ML PREDICTION")
    if "error" in ml:
        print(f"     Error:          {ml['error']}")
    else:
        print(f"     Prediction:     {ml.get('label', 'N/A')} ({ml.get('prediction', '?')})")
        print(f"     Confidence:     {ml.get('confidence', 0)}")

    vd = trace.get("verdict", {})
    print(f"\n  10. FINAL VERDICT")
    print(f"     Score:          {vd.get('score', 0)}/100")
    print(f"     Verdict:        {vd.get('verdict', 'N/A')}")
    print(f"     Trusted source: {vd.get('is_trusted_source', False)}")
    print(f"     Conditions:     {vd.get('conditions_met', [])}")
    bd = vd.get("breakdown", {})
    if bd:
        print(f"\n     Contributions:")
        for key, data in bd.items():
            label = key.replace("_", " ").title()
            raw = data.get("raw", "?")
            weighted = data.get("weighted", 0)
            print(f"       {label:<22} raw={raw:<8} weighted={weighted:.2f}")
    print(f"\n     Explanations:")
    for i, e in enumerate(vd.get("explanations", []), 1):
        print(f"       {i}. {e}")
    print(f"{sep}\n")


if __name__ == "__main__":
    import json
    test_input = sys.argv[1] if len(sys.argv) > 1 else input("Enter article text or URL: ")
    trace = audit_article(test_input)
    print_audit(trace)
    with open("audit_trace.json", "w") as f:
        json.dump(trace, f, indent=2, default=str)
    print("\nTrace saved to audit_trace.json")
