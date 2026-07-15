"""
VALIDATION REPORT - Evidence Quality Score Integration

Compares the verdict engine output for trusted publishers and regional
sources with the new evidence quality scoring system.

Usage:
    python validate_evidence_quality.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.evidence_quality import compute_evidence_quality
from src.verdict_engine import generate_verdict

# Old weights for before/after comparison
OLD_WEIGHTS = {
    "source_reputation": 35,
    "external_evidence": 25,
    "fact_check": 15,
    "timeline": 10,
    "manipulation": 5,
    "headline": 5,
    "ml_prediction": 5,
}

TEST_SCENARIOS = [
    {
        "label": "BBC.co.uk article",
        "source_info": {"domain": "bbc.com", "score": 95, "label": "Highly Trusted"},
        "evidence": [
            {"source": "Reuters", "title": "UK economy shows signs of recovery", "url": "http://reuters.com/1"},
            {"source": "Associated Press", "title": "British GDP rises unexpectedly", "url": "http://apnews.com/1"},
            {"source": "The Guardian", "title": "UK economic outlook improves", "url": "http://theguardian.com/1"},
            {"source": "BBC", "title": "London markets rally on news", "url": "http://bbc.com/1"},
            {"source": "Financial Times", "title": "Sterling strengthens after data", "url": "http://ft.com/1"},
        ],
    },
    {
        "label": "Reuters article",
        "source_info": {"domain": "reuters.com", "score": 98, "label": "Highly Trusted"},
        "evidence": [
            {"source": "AP", "title": "Global trade deal reached", "url": "http://apnews.com/2"},
            {"source": "BBC News", "title": "World leaders sign accord", "url": "http://bbc.com/2"},
            {"source": "Al Jazeera", "title": "Trade agreement finalized", "url": "http://aljazeera.com/2"},
            {"source": "DW", "title": "European markets react to deal", "url": "http://dw.com/2"},
            {"source": "France 24", "title": "Trade pact wins approval", "url": "http://france24.com/2"},
        ],
    },
    {
        "label": "AP News article",
        "source_info": {"domain": "apnews.com", "score": 97, "label": "Highly Trusted"},
        "evidence": [
            {"source": "Reuters", "title": "Senate passes infrastructure bill", "url": "http://reuters.com/3"},
            {"source": "The New York Times", "title": "Historic infrastructure vote", "url": "http://nytimes.com/3"},
            {"source": "Washington Post", "title": "Bipartisan deal reached", "url": "http://washingtonpost.com/3"},
            {"source": "Reuters", "title": "Infrastructure bill analysis", "url": "http://reuters.com/3b"},
            {"source": "CNN", "title": "What the bill means for voters", "url": "http://cnn.com/3"},
        ],
    },
    {
        "label": "Al Jazeera article",
        "source_info": {"domain": "aljazeera.com", "score": 90, "label": "Highly Trusted"},
        "evidence": [
            {"source": "Reuters", "title": "Middle East peace talks resume", "url": "http://reuters.com/4"},
            {"source": "AP", "title": "Diplomatic breakthrough in region", "url": "http://apnews.com/4"},
            {"source": "The Guardian", "title": "Negotiators optimistic", "url": "http://theguardian.com/4"},
            {"source": "BBC", "title": "Ceasefire holds for third day", "url": "http://bbc.com/4"},
        ],
    },
    {
        "label": "The Hindu (Indian publisher)",
        "source_info": {"domain": "hindu.com", "score": 82, "label": "Trusted"},
        "evidence": [
            {"source": "Reuters", "title": "India GDP growth accelerates", "url": "http://reuters.com/5"},
            {"source": "Times of India", "title": "Economic reforms gaining pace", "url": "http://timesofindia.indiatimes.com/5"},
            {"source": "NDTV", "title": "Government announces new policy", "url": "http://ndtv.com/5"},
            {"source": "The Hindu", "title": "Local analysis of budget impact", "url": "http://hindu.com/5"},
        ],
    },
    {
        "label": "Nation.africa (Kenyan)",
        "source_info": {"domain": "nation.africa", "score": 80, "label": "Trusted"},
        "evidence": [
            {"source": "Reuters", "title": "East African trade bloc expands", "url": "http://reuters.com/6"},
            {"source": "Africanews", "title": "Regional integration advances", "url": "http://africanews.com/6"},
            {"source": "The East African", "title": "Cross-border trade increases", "url": "http://theeastafrican.co.ke/6"},
            {"source": "Daily Nation", "title": "Kenya benefits from new pact", "url": "http://nation.africa/6"},
        ],
    },
    {
        "label": "The Citizen (South Africa)",
        "source_info": {"domain": "citizen.co.za", "score": 75, "label": "Trusted"},
        "evidence": [
            {"source": "AP", "title": "SA mining output rises", "url": "http://apnews.com/7"},
            {"source": "News24", "title": "Gold employment grows", "url": "http://news24.com/7"},
            {"source": "Mail and Guardian", "title": "Energy crisis deepens", "url": "http://mg.co.za/7"},
            {"source": "The Citizen", "title": "Local government responds", "url": "http://citizen.co.za/7"},
        ],
    },
    {
        "label": "CCTV (Chinese state media)",
        "source_info": {"domain": "cctv.com", "score": 45, "label": "Low Reliability"},
        "evidence": [
            {"source": "Xinhua", "title": "China economy leads global growth", "url": "http://xinhuanet.com/1"},
            {"source": "Global Times", "title": "Media bias against China", "url": "http://globaltimes.cn/1"},
            {"source": "CCTV", "title": "Infrastructure projects expand", "url": "http://cctv.com/1"},
            {"source": "China Daily", "title": "Trade surplus widens", "url": "http://chinadaily.com.cn/1"},
        ],
    },
    {
        "label": "Clickbait blog (unmatched)",
        "source_info": {"domain": "clickbait.example.com", "score": 25, "label": "Low Reliability"},
        "evidence": [
            {"source": "Unreliable Blog", "title": "You wont believe what happened", "url": "http://blog.example.com/1"},
            {"source": "Daily Buzz", "title": "Doctors hate this one weird trick", "url": "http://buzz.example.com/2"},
            {"source": "Viral News Network", "title": "This changes EVERYTHING", "url": "http://viral.example.com/3"},
        ],
    },
    {
        "label": "Mixed quality evidence",
        "source_info": {"domain": "forum.example.com", "score": 35, "label": "Low Reliability"},
        "evidence": [
            {"source": "Reuters", "title": "Scientific study published", "url": "http://reuters.com/8"},
            {"source": "Unknown Forum", "title": "My personal theory about this", "url": "http://forum.example.com/1"},
            {"source": "Anonymous", "title": "Someone told me this is true", "url": "http://anon.example.com/2"},
        ],
    },
]


def run_scenario(scenario):
    info = scenario["source_info"]
    ev = scenario["evidence"]
    eq = compute_evidence_quality(ev)
    v = generate_verdict(
        source_info=info, prediction=1, confidence=0.85,
        matched_sources=3, total_sources=5,
        fact_result={"verdict": "Partially Supported", "sources": 2, "results": {}},
        evidence=ev,
        sentiment_result={"polarity": 0.1, "sensational_words": [], "manipulation_risk": "Low"},
        risk_result={"risk_categories": ["General"], "high_risk": False, "risk_level": "Low"},
        timeline_result={"status": "Recent", "years_old": 0, "is_old_news": False},
        headline_result={"headline": "Test", "risk": "Low", "score": 0, "reasons": []},
        rewrite_result={"similarity": 75.0, "risk": "Low", "explanation": "Matches trusted sources"},
        source_comparison_result={"agreement": 85, "classification": "High Agreement", "sources_checked": 4},
    )
    bd = v.get("breakdown", {})
    return {
        "evidence_quality": eq,
        "verdict_score": v["score"],
        "verdict": v["verdict"],
        "breakdown": {
            "source_reputation": bd.get("source_reputation", {}).get("weighted", 0),
            "external_evidence": bd.get("external_evidence", {}).get("weighted", 0),
            "evidence_quality": bd.get("evidence_quality", {}).get("weighted", 0),
            "evidence_quality_label": bd.get("evidence_quality", {}).get("label", "N/A"),
            "evidence_quality_raw": bd.get("evidence_quality", {}).get("raw", 0),
            "unique_sources": bd.get("evidence_quality", {}).get("unique_sources", 0),
        },
    }


def simulate_old_verdict(scenario):
    """Simulate what the verdict engine would return with OLD weights (no evidence quality)."""
    info = scenario["source_info"]
    ev = scenario["evidence"]
    ev_count = len(ev)
    pct = min(ev_count / 10.0, 1.0) * 100
    src_weighted = info["score"] * (OLD_WEIGHTS["source_reputation"] / 100.0)
    evid_weighted = pct * (OLD_WEIGHTS["external_evidence"] / 100.0)
    fc_weighted = 60 * (OLD_WEIGHTS["fact_check"] / 100.0)
    tl_weighted = 100 * (OLD_WEIGHTS["timeline"] / 100.0)
    manip_weighted = 100 * (OLD_WEIGHTS["manipulation"] / 100.0)
    hl_weighted = 100 * (OLD_WEIGHTS["headline"] / 100.0)
    ml_weighted = 85 * (OLD_WEIGHTS["ml_prediction"] / 100.0)
    old_total = round(src_weighted + evid_weighted + fc_weighted + tl_weighted
                      + manip_weighted + hl_weighted + ml_weighted, 2)
    return old_total


if __name__ == "__main__":
    print("=" * 100)
    print("  VALIDATION REPORT - Evidence Quality Score (Before vs After)")
    print("=" * 100)
    
    # New system table
    print("\n  --- NEW SYSTEM (with evidence_quality=10%, external_evidence=15%) ---")
    hdr = f"{'Test Case':<35} {'Src':<5} {'#Ev':<4} {'Qual':<5} {'Label':<12} {'Q-Wt':<6} {'Final':<6} {'Verdict':<22}"
    print(hdr)
    print("-" * 100)

    new_results = []
    for s in TEST_SCENARIOS:
        r = run_scenario(s)
        label = s["label"]
        src_score = s["source_info"]["score"]
        ev_count = len(s["evidence"])
        eq_score = r["evidence_quality"]["score"]
        eq_label = r["evidence_quality"]["label"]
        eq_wt = r["breakdown"]["evidence_quality"]
        final = r["verdict_score"]
        verdict = r["verdict"]
        row = f"{label:<35} {src_score:<5} {ev_count:<4} {eq_score:<5} {eq_label:<12} {eq_wt:<6.2f} {final:<6} {verdict:<22}"
        print(row)
        old_final = simulate_old_verdict(s)
        new_results.append({
            "test_case": label,
            "source_score": src_score,
            "evidence_count": ev_count,
            "evidence_quality_raw": eq_score,
            "evidence_quality_label": eq_label,
            "evidence_quality_weighted": eq_wt,
            "final_verdict_score_new": final,
            "final_verdict_new": verdict,
            "final_verdict_score_old": old_final,
            "quality_breakdown": r["evidence_quality"]["breakdown"],
            "unmatched_sources": r["evidence_quality"]["unmatched"],
        })

    # Before/After comparison table
    print(f"\n  --- BEFORE vs AFTER COMPARISON ---")
    cmp_hdr = f"{'Test Case':<35} {'Old Score':<10} {'New Score':<10} {'Delta':<8} {'Old Verdict':<22} {'New Verdict':<22}"
    print(cmp_hdr)
    print("-" * 100)
    for nr in new_results:
        old = nr["final_verdict_score_old"]
        new = nr["final_verdict_score_new"]
        delta = new - old
        delta_str = f"{delta:+.1f}"
        # Simple old verdict estimation based on score
        if old >= 90:
            old_v = "Highly Credible"
        elif old >= 75:
            old_v = "Likely Credible"
        elif old >= 50:
            old_v = "Mixed Evidence"
        elif old >= 30:
            old_v = "Suspicious"
        else:
            old_v = "Highly Suspicious"
        print(f"{nr['test_case']:<35} {old:<10.2f} {new:<10.2f} {delta_str:<8} {old_v:<22} {nr['final_verdict_new']:<22}")

    print(f"\n{'=' * 100}")
    print("  SUMMARY - Impact of Evidence Quality Score")
    print(f"{'=' * 100}")
    
    trusted_gain = 0
    low_quality_loss = 0
    for nr in new_results:
        tc = nr["test_case"]
        delta = nr["final_verdict_score_new"] - nr["final_verdict_score_old"]
        if tc in ["BBC.co.uk article", "Reuters article", "AP News article", "Al Jazeera article"]:
            print(f"  Trusted wire: {tc:<35} old={nr['final_verdict_score_old']:.1f} -> new={nr['final_verdict_score_new']:.1f} ({delta:+.1f})")
            trusted_gain += delta
        elif tc in ["The Hindu (Indian publisher)", "Nation.africa (Kenyan)", "The Citizen (South Africa)"]:
            print(f"  Regional:     {tc:<35} old={nr['final_verdict_score_old']:.1f} -> new={nr['final_verdict_score_new']:.1f} ({delta:+.1f})")
        elif "clickbait" in tc.lower() or "mixed" in tc.lower() or "cctv" in tc.lower():
            print(f"  Low quality:  {tc:<35} old={nr['final_verdict_score_old']:.1f} -> new={nr['final_verdict_score_new']:.1f} ({delta:+.1f})")
            low_quality_loss += delta

    print(f"\n{'=' * 100}")
    print(f"  Trusted sources average delta: {trusted_gain / 4:.1f} points")
    print(f"  Low-quality sources avg delta: {low_quality_loss / 4:.1f} points")
    print(f"  {'=' * 100}")

    with open("validate_evidence_quality_results.json", "w") as f:
        json.dump(new_results, f, indent=2)
    print(f"\n  Results saved to validate_evidence_quality_results.json")
