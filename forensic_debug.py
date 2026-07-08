"""
FORENSIC DIAGNOSTIC SCRIPT — Live Pipeline Analysis
Temporary script. Does NOT modify any existing code.
"""
import sys, os, json, pickle
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.social_media import is_url
from src.source_rating import get_source_rating, get_domain
from src.url_extractor import extract_article
from src.analyzer import analyze_article
from src.fact_checker import fact_check
from src.entity_extractor import extract_entities
from src.evidence_finder import find_evidence
from src.similarity_checker import calculate_similarity
from src.sentiment_analyzer import analyze_sentiment
from src.virality_detector import calculate_virality
from src.risk_detector import detect_risk
from src.timeline_checker import check_timeline
from src.source_comparison import compare_sources
from src.headline_checker import analyze_headline
from src.rewrite_detector import detect_rewrite
from src.verdict_engine import generate_verdict, TRUSTED_PUBLISHERS
from src.preprocess import clean_text
from difflib import SequenceMatcher

model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

TEST_CASES = [
    ("1-BBC", "https://www.bbc.com/news/articles/c20r18x8x05o"),
    ("2-AP", "https://apnews.com/article/senate-iran-war-powers-resolution-trump-7462a9a561103f531d995aac91f9fc96"),
    ("3-REUTERS", "https://www.reuters.com/world/asia-pacific/gold-set-become-australias-second-biggest-resource-earner-2025-10-06/"),
    ("4-FAKE", "BREAKING: Haitian immigrants in Springfield, Ohio are stealing and eating people's pet cats and dogs! This is outrageous and the government is covering it up. Multiple residents have reported their pets going missing. The police refuse to investigate because they're afraid of being called racist. Share this before it gets taken down! WAKE UP AMERICA!"),
    ("5-FACEBOOK", "URGENT: Shocking new evidence reveals that presidential candidate Ivan Korcok was a secret police informant for the communist StB during his university years! These classified documents prove he collaborated with the regime. The mainstream media won't report on this because they're protecting him. This is the truth about what kind of leader he would be. Share with everyone you know!")
]

def kv(k, v):
    print(f"  {k}: {v}")

def sep(t):
    print(f"\n{'='*70}\n  {t}\n{'='*70}")

def run(label, input_text):
    print(f"\n\n{'#'*80}")
    print(f"#  {label}")
    print(f"{'#'*80}")

    is_url_input = is_url(input_text)
    print(f"\nInput: {'URL' if is_url_input else 'TEXT'}")
    if is_url_input:
        print(f"URL: {input_text}")

    # STATE
    article_title = "User-Submitted Text"
    text_to_analyze = input_text
    source_info = {"domain": "N/A", "score": 50, "label": "Unknown"}
    publish_date = None
    evidence = []
    fact_result = {"claim": "", "verdict": "Unverified", "sources": 0, "results": {}}
    claim_text = ""
    results_dict = {}
    total_results = 0
    prediction = 0
    confidence = 0.5

    # --- URL EXTRACTION ---
    if is_url_input:
        sep("URL EXTRACTION")
        article = extract_article(input_text)
        st = article.get("source_type", "failed")
        kv("Success", article.get("success", False))
        kv("Source Type", st)
        if not article.get("success", False):
            kv("Error", article.get("error", "N/A"))
            return {"label": label, "error": article.get("error", "Extraction failed")}

        if st == "search_fallback":
            text_to_analyze = (article.get("title", "") + " " + article.get("text", "")).strip()
            article_title = article.get("title", "Fallback Article")
            publish_date = None
            kv("Fallback Title", article_title)
            kv("Fallback Snippet", article.get("text", "")[:200])
        else:
            text_to_analyze = article.get("text", "")
            article_title = article.get("title", "Untitled")
            publish_date = article.get("publish_date")
            kv("Title", article_title)
            kv("Extracted Length", len(text_to_analyze))
            kv("Publish Date", str(publish_date) if publish_date else "None")
            kv("Authors", article.get("authors", []))

        # --- SOURCE RATING ---
        sep("SOURCE RATING")
        source_info = get_source_rating(input_text)
        domain = get_domain(input_text)
        kv("Domain", domain)
        kv("Source Score", source_info["score"])
        kv("Source Label", source_info["label"])
        kv("In TRUSTED_PUBLISHERS", domain in TRUSTED_PUBLISHERS if domain else False)

    wc = len(text_to_analyze.split())
    kv("Word Count", wc)

    # --- ML MODEL ---
    sep("ML MODEL PREDICTION")
    cleaned = clean_text(text_to_analyze)
    vectorized = vectorizer.transform([cleaned])
    prediction = int(model.predict(vectorized)[0])
    probs = model.predict_proba(vectorized)[0]
    confidence = max(probs)
    kv("Prediction", "REAL (1)" if prediction == 1 else "FAKE (0)")
    kv("Probabilities", f"fake={probs[0]:.4f}, real={probs[1]:.4f}")
    kv("Confidence", f"{confidence:.4f}")

    # --- ML PREDICTION (no API calls) ---
    sep("ML PREDICTION (no API calls)")
    kv("Prediction", "REAL (1)" if prediction == 1 else "FAKE (0)")
    kv("Confidence", f"{confidence:.4f}")
    kv("Status", "ML inference only — API calls handled by evidence_finder exclusively")

    # --- FACT CHECK + CLAIM ---
    sep("FACT CHECK & CLAIM EXTRACTION")
    try:
        fact_result = fact_check(text_to_analyze, evidence=evidence)
        claim_text = fact_result["claim"]
        kv("Extracted Claim", claim_text[:200])
        kv("Verdict", fact_result["verdict"])
        kv("Matched Sources", fact_result["sources"])
        kv("API Results", str(fact_result.get("results", {})))
    except Exception as e:
        kv("Error", str(e))

    # --- ENTITIES ---
    sep("ENTITY EXTRACTION")
    try:
        ents = extract_entities(text_to_analyze)
        kv("People", ents.get("people", [])[:5])
        kv("Orgs", ents.get("organizations", [])[:5])
        kv("Locations", ents.get("locations", [])[:5])
        kv("Dates", ents.get("dates", [])[:5])
    except Exception as e:
        kv("Error", str(e))

    # --- EVIDENCE RETRIEVAL ---
    sep("EVIDENCE RETRIEVAL")
    try:
        if is_url_input:
            ev_query = article_title if article_title and article_title not in ("User-Submitted Text", "Untitled Article", "Fallback Article") else (claim_text if claim_text else " ".join(text_to_analyze.split()[:10]))
        else:
            ev_query = claim_text if claim_text else " ".join(text_to_analyze.split()[:10])

        kv("Search Query", ev_query[:100])
        evidence = find_evidence(ev_query)
        kv("Total Found", len(evidence))

        if evidence:
            ev_list = []
            for i, e in enumerate(evidence[:8], 1):
                s = e.get("source", "?"); t = e.get("title", "")[:100]; u = e.get("url", "")[:80]
                print(f"\n  Evidence #{i}: [{s}] {t}")
                print(f"    URL: {u}")
                ev_list.append({"source": s, "title": t, "url": u})
        else:
            print("  NO EVIDENCE FOUND")
            # Try fallback with claim
            if claim_text:
                more = find_evidence(claim_text)
                kv("Retry with claim", f"{len(more)} results")
    except Exception as e:
        kv("Error", str(e))

    # --- SIMILARITY ---
    sep("SIMILARITY ANALYSIS")
    sim_claim = claim_text if claim_text else text_to_analyze[:200]
    sim_score = calculate_similarity(sim_claim, text_to_analyze) if claim_text else 0
    kv("Comparing", "Claim vs Full Article Text")
    kv("Claim chars", len(sim_claim))
    kv("Article chars", len(text_to_analyze))
    kv("SequenceMatcher", f"{sim_score}%")
    print("  → Low score expected: claim (~30 words) vs article (~500+ words)")

    # Claim vs evidence titles
    ev_sims = []
    for i, e in enumerate(evidence[:8], 1):
        t = e.get("title", "")
        if t:
            s = calculate_similarity(sim_claim, t)
            ev_sims.append(s)
            print(f"  vs Ev#{i}: {s:.1f}%")
    if ev_sims:
        print(f"  Average vs evidence: {sum(ev_sims)/len(ev_sims):.2f}%")

    # --- SENTIMENT ---
    sep("SENTIMENT ANALYSIS")
    sr = analyze_sentiment(text_to_analyze)
    kv("Polarity", f"{sr.get('polarity', 0):.2f}")
    kv("Manipulation Risk", sr.get("manipulation_risk", "Low"))
    kv("Sensational Words", sr.get("sensational_words", []))

    # --- VIRALITY ---
    sep("VIRALITY DETECTION")
    vr = calculate_virality(results_dict)
    kv("Total (API sums)", vr.get("mentions", 0))
    kv("Level", vr.get("level", "Low"))
    print("  NOTE: sums API result counts, NOT actual social media mentions")

    # --- RISK ---
    sep("RISK DETECTION")
    rr = detect_risk(text_to_analyze)
    kv("Categories", rr.get("risk_categories", ["General"]))
    kv("High Risk", rr.get("high_risk", False))

    # --- TIMELINE ---
    sep("TIMELINE ANALYSIS")
    tl = check_timeline(publish_date)
    kv("Publish Date", str(publish_date) if publish_date else "None")
    kv("Status", tl.get("status", "Unknown"))
    kv("Years Old", tl.get("years_old"))

    # --- SOURCE COMPARISON ---
    sep("SOURCE COMPARISON")
    sc = compare_sources(claim_text, evidence)
    kv("Agreement %", f"{sc.get('agreement', 0)}%")
    kv("Classification", sc.get("classification", "Low Agreement"))
    kv("Sources Checked", sc.get("sources_checked", 0))
    if evidence and claim_text:
        print("\n  Individual SequenceMatcher scores (claim vs each evidence title):")
        for i, e in enumerate(evidence[:8], 1):
            t = e.get("title", "")
            if t:
                r = SequenceMatcher(None, claim_text.lower(), t.lower()).ratio()
                print(f"    Ev#{i}: {r*100:.1f}%")
        print("  ⚠️ Measures STRING similarity, not factual agreement!")
        print("  Different wording of same event => LOW score")

    # --- HEADLINE ---
    sep("HEADLINE ANALYSIS")
    hl = analyze_headline(article_title)
    kv("Headline", article_title[:80])
    kv("Risk", hl.get("risk", "Low"))
    kv("Score", f"{hl.get('score', 0)}/100")
    for r in hl.get("reasons", []):
        print(f"    • {r}")

    # --- REWRITE DETECTOR ---
    sep("REWRITE DETECTOR")
    rw = detect_rewrite(claim_text, evidence)
    kv("Similarity (claim vs evidence titles)", f"{rw.get('similarity', 0)}%")
    kv("Manipulation Risk", rw.get("risk", "High"))
    kv("Explanation", rw.get("explanation", "")[:120])
    if not evidence:
        print("  ❌ No evidence => similarity=0% => default Risk=High")
    if evidence and claim_text:
        print("  ⚠️ IDENTICAL computation to source_comparison! Double-counted signal.")

    # --- VERDICT ENGINE ---
    sep("VERDICT ENGINE")
    matched_sources = sum(1 for v in results_dict.values() if v > 0) if results_dict else 0
    total_sources = len(results_dict) if results_dict else 0

    adapted_risk = {**rr, "risk_level": "High" if rr.get("high_risk") else ("Medium" if len(rr.get("risk_categories", [])) > 1 else "Low")}
    adapted_timeline = {**tl, "is_old_news": (tl.get("status") == "Old Article")}

    v = generate_verdict(
        source_info=source_info,
        prediction=prediction,
        confidence=confidence,
        matched_sources=matched_sources,
        total_sources=total_sources if total_sources > 0 else 1,
        fact_result=fact_result,
        evidence=evidence,
        sentiment_result=sr,
        risk_result=adapted_risk,
        timeline_result=adapted_timeline,
        headline_result=hl,
        rewrite_result=rw,
        source_comparison_result=sc
    )

    kv("Is Trusted Source", v.get("is_trusted_source", False))
    kv("Conditions Met", v.get("conditions_met", []))

    bd = v.get("breakdown", {})
    print(f"\n  {'Signal':<22} {'Raw':<18} {'Weight':<10} {'Weighted':<10}")
    print(f"  {'-'*22} {'-'*18} {'-'*10} {'-'*10}")
    for key, data in bd.items():
        label = key.replace("_", " ").title()
        raw = data.get("raw", "N/A")
        w = data.get("weight", 0)
        wted = data.get("weighted", 0)
        if isinstance(raw, float):
            print(f"  {label:<22} {raw:<18.1f} {w:<10}% {wted:<10.2f}")
        else:
            print(f"  {label:<22} {str(raw):<18} {w:<10}% {wted:<10.2f}")

    print(f"\n  {'FINAL':<22}                          {v.get('score', 0)}")
    print(f"  {'VERDICT':<22}                          {v.get('verdict', 'N/A')}")
    print("\n  Explanations:")
    for e in v.get("explanations", []):
        print(f"    • {e}")

    # Trusted source override analysis
    if v.get("is_trusted_source", False):
        signals = []
        if rw.get("risk") == "High": signals.append("manipulation")
        if hl.get("risk") == "High": signals.append("clickbait")
        if fact_result.get("verdict") == "Unverified" and fact_result.get("sources") == 0: signals.append("failed_fact_check")
        if confidence < 0.6: signals.append("low_confidence")
        print(f"\n  🔍 OVERRIDE ANALYSIS:")
        print(f"  Neg signals: {signals} (count={len(signals)}, need <2)")
        if len(signals) >= 2:
            print(f"  ❌ OVERRIDE BLOCKED!")
        else:
            print(f"  ✅ OVERRIDE ACTIVE => score >= 75")

    # --- SUMMARY ---
    sep("FINAL SUMMARY")
    print(f"  Source: {source_info.get('score', 0)}/100 ({source_info.get('label', 'N/A')})")
    print(f"  Evidence: {len(evidence)} articles")
    print(f"  Agreement: {sc.get('agreement', 0)}% ({sc.get('classification', 'N/A')})")
    print(f"  Manipulation: {rw.get('risk', 'N/A')} (sim={rw.get('similarity', 0)}%)")
    print(f"  Headline: {hl.get('risk', 'N/A')} (score={hl.get('score', 0)})")
    print(f"  Timeline: {tl.get('status', 'Unknown')}")
    print(f"  ML: {'REAL' if prediction==1 else 'FAKE'} (conf={confidence:.2%})")
    print(f"  Fact Check: {fact_result.get('verdict', 'N/A')} ({fact_result.get('sources', 0)} sources)")
    print(f"  {'─'*50}")
    print(f"  FINAL: {v.get('score', 'N/A')}/100 — {v.get('verdict', 'N/A')}")

    return {
        "label": label,
        "source": source_info,
        "evidence_count": len(evidence),
        "agreement": sc.get("agreement", 0),
        "agreement_class": sc.get("classification", "N/A"),
        "manipulation_risk": rw.get("risk", "N/A"),
        "headline_risk": hl.get("risk", "N/A"),
        "timeline_status": tl.get("status", "Unknown"),
        "ml_prediction": prediction,
        "ml_confidence": confidence,
        "fact_check_verdict": fact_result.get("verdict", "N/A"),
        "final_score": v.get("score", 0),
        "final_verdict": v.get("verdict", "N/A"),
        "is_trusted": v.get("is_trusted_source", False),
        "explanations": v.get("explanations", [])
    }

if __name__ == "__main__":
    all_results = {}
    for label, text in TEST_CASES:
        try:
            all_results[label] = run(label, text)
        except Exception as e:
            import traceback
            print(f"\n❌ CRITICAL ERROR in {label}: {e}")
            traceback.print_exc()
            all_results[label] = {"error": str(e)}

    with open("forensic_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Results saved to forensic_results.json")

    # Final comparison table
    print(f"\n\n{'='*80}")
    print("  COMPARISON TABLE — All 5 Articles")
    print(f"{'='*80}")
    print(f"{'Article':<28} {'Trust':<6} {'Evid':<5} {'Agree':<7} {'Manip':<7} {'Head':<7} {'ML':<8} {'Score':<7} {'Verdict':<18}")
    print(f"{'-'*90}")
    for label, text in TEST_CASES:
        r = all_results.get(label, {})
        if "error" in r:
            print(f"{label:<28} ERROR: {r['error']}")
            continue
        src = r.get("source", {}).get("score", "?")
        ev = r.get("evidence_count", "?")
        ag = r.get("agreement", "?")
        mp = r.get("manipulation_risk", "?")
        hl = r.get("headline_risk", "?")
        ml = "REAL" if r.get("ml_prediction") == 1 else "FAKE"
        sc = r.get("final_score", "?")
        vd = r.get("final_verdict", "?")
        print(f"{label:<28} {str(src):<6} {str(ev):<5} {str(ag)+'%':<7} {str(mp):<7} {str(hl):<7} {ml:<8} {str(sc):<7} {str(vd):<18}")
