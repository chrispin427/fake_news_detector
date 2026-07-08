"""
VALIDATION TEST SCRIPT - Backend Reliability Upgrade

Tests the improvements made to evidence_finder, rewrite_detector,
source_comparison, timeline_checker, and verdict_engine.
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 70)
print("  VALIDATION TESTS - Backend Reliability Upgrade")
print("=" * 70)

passed = 0
failed = 0
results = []


def run_test(name, fn):
    global passed, failed
    print(f"\n--- {name} ---")
    try:
        fn()
        print(f"  [PASS] {name}")
        passed += 1
        results.append((name, "PASS"))
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        failed += 1
        results.append((name, f"FAIL: {e}"))


# ===== TEST 1: GNews query truncation =====
def test_gnews_truncation():
    from src.evidence_finder import _truncate_query

    short = "UK Parliament votes on new trade deal"
    result = _truncate_query(short)
    assert result == short, f"Short query truncated: {result}"

    long_q = "The quick brown fox jumps over the lazy dog and then " * 20
    result = _truncate_query(long_q)
    assert len(result) <= 200, f"Too long: {len(result)} chars"
    print(f"  Truncated from {len(long_q)} to {len(result)} chars")

    boundary = "A" * 200
    result = _truncate_query(boundary)
    assert len(result) == 200, f"Boundary modified: {len(result)}"


run_test("Test 1: GNews truncation", test_gnews_truncation)


# ===== TEST 2: URL normalisation & dedup =====
def test_url_dedup():
    from src.evidence_finder import _normalise_url, _title_similarity

    assert _normalise_url("https://www.bbc.com/news") == "bbc.com/news"
    assert _normalise_url("http://BBC.com/news/") == "bbc.com/news"
    assert _normalise_url("https://www.example.com/path/") == "example.com/path"

    sim = _title_similarity("UK votes on trade deal", "UK votes on new trade deal")
    assert sim > 0.85, f"Similar titles not matched: {sim}"

    sim2 = _title_similarity("UK votes on trade deal", "Weather forecast for London today")
    assert sim2 < 0.5, f"Different titles scored too high: {sim2}"


run_test("Test 2: URL dedup", test_url_dedup)


# ===== TEST 3: evidence_finder smoke =====
def test_evidence_smoke():
    from src.evidence_finder import find_evidence
    evidence = find_evidence("UK Parliament votes on trade deal")
    print(f"  find_evidence returned {len(evidence)} articles (may be 0 if no keys)")


run_test("Test 3: find_evidence smoke", test_evidence_smoke)


# ===== TEST 4: rewrite_detector Unknown risk =====
def test_unknown_risk():
    from src.rewrite_detector import detect_rewrite

    r = detect_rewrite("", [])
    assert r["risk"] == "Unknown", f"Expected Unknown, got {r['risk']}"
    assert "No evidence available" in r["explanation"]

    r = detect_rewrite("UK votes on trade deal", [])
    assert r["risk"] == "Unknown", f"Expected Unknown, got {r['risk']}"

    r = detect_rewrite("UK votes on trade deal", [
        {"title": "UK Parliament votes on new trade deal agreement"}
    ])
    assert r["risk"] in ("Low", "Medium", "High"), f"Unexpected risk: {r['risk']}"
    print(f"  With evidence: risk={r['risk']}, similarity={r['similarity']}%")


run_test("Test 4: Unknown risk", test_unknown_risk)


# ===== TEST 5: source_comparison keyword overlap =====
def test_keyword_overlap():
    from src.source_comparison import compare_sources

    claim = "Senate votes to advance resolution limiting presidential war powers"
    evidence = [
        {"title": "US Senate Advances Bill to Restrict President's Military Authority"},
        {"title": "Senate Committee Approves War Powers Resolution"},
        {"title": "US lawmakers move to limit presidential war-making ability"},
        {"title": "Senate votes to advance Iran war powers resolution"},
        {"title": "Congressional leaders back new limits on executive military action"},
    ]

    r = compare_sources(claim, evidence)
    agreement = r["agreement"]
    debug = r.get("debug", {})
    kw_avg = debug.get("avg_keyword_similarity", 0)
    str_avg = debug.get("avg_string_similarity", 0)

    print(f"  Agreement: {agreement}%, Class: {r['classification']}")
    print(f"  Keyword avg: {kw_avg}%, String avg: {str_avg}%")

    assert agreement >= 30, f"Agreement too low: {agreement}%"
    assert "method" in debug, "Missing debug method"
    assert "avg_keyword_similarity" in debug, "Missing keyword avg"


run_test("Test 5: keyword overlap", test_keyword_overlap)


# ===== TEST 6: timeline_checker Unknown neutral =====
def test_timeline_unknown():
    from src.timeline_checker import check_timeline

    r = check_timeline(None)
    assert r["status"] == "Unknown"
    dbg = r.get("debug", {})
    impact = dbg.get("score_impact", "")
    assert "neutral" in impact, f"Expected neutral, got {impact}"
    print(f"  Status: {r['status']}, Impact: {impact}")


run_test("Test 6: Unknown neutral timeline", test_timeline_unknown)


# ===== TEST 7: verdict_engine Unknown manipulation scoring =====
def test_unknown_manipulation():
    from src.verdict_engine import _score_manipulation

    result = _score_manipulation({"risk": "Unknown"})
    score, pct, risk = result
    assert risk == "Unknown"
    assert pct == 100, f"Expected 100% for Unknown, got {pct}%"
    print(f"  Unknown -> pct={pct}% (neutral)")

    result = _score_manipulation({"risk": "High"})
    score, pct, risk = result
    assert pct == 0, f"Expected 0% for High, got {pct}%"
    print(f"  High -> pct={pct}% (penalty preserved)")


run_test("Test 7: Unknown manipulation scoring", test_unknown_manipulation)


# ===== TEST 8: verdict_engine Unknown timeline scoring =====
def test_unknown_timeline():
    from src.verdict_engine import _score_timeline

    result = _score_timeline({"status": "Unknown"})
    score, pct, status = result
    assert status == "Unknown"
    assert pct == 100, f"Expected 100% for Unknown, got {pct}%"
    print(f"  Unknown -> pct={pct}% (neutral)")

    result = _score_timeline({"status": "Recent"})
    score, pct, status = result
    assert pct == 100

    result = _score_timeline({"status": "Old Article"})
    score, pct, status = result
    assert pct == 30, f"Expected 30% for Old, got {pct}%"
    print(f"  Old Article -> pct={pct}% (penalty preserved)")


run_test("Test 8: Unknown timeline scoring", test_unknown_timeline)


# ===== TEST 9: debug_audit smoke =====
def test_debug_audit():
    from src.debug_audit import audit_article

    trace = audit_article("UK Parliament votes on a new trade deal agreement today.")
    expected_keys = [
        "input", "source", "claim", "evidence", "source_agreement",
        "rewrite", "fact_check", "timeline", "sentiment", "headline",
        "ml", "verdict"
    ]
    for key in expected_keys:
        assert key in trace, f"Missing key: {key}"
    print(f"  audit_article returns all {len(expected_keys)} sections")


run_test("Test 9: debug_audit smoke", test_debug_audit)


# ===== TEST 10: E2E verdict with Unknown signals =====
def test_e2e_unknown():
    from src.verdict_engine import generate_verdict

    source_info = {"domain": "bbc.com", "score": 95, "label": "Highly Trusted"}
    rewrite_result = {"similarity": 0.0, "risk": "Unknown", "explanation": "No evidence"}
    timeline_result = {"status": "Unknown", "years_old": None, "is_old_news": False}

    verdict = generate_verdict(
        source_info=source_info,
        prediction=1,
        confidence=0.85,
        matched_sources=0,
        total_sources=4,
        fact_result={"verdict": "Unverified", "sources": 0, "results": {}},
        evidence=[],
        sentiment_result={"polarity": 0, "sensational_words": [], "manipulation_risk": "Low"},
        risk_result={"risk_categories": ["General"], "high_risk": False, "risk_level": "Low"},
        timeline_result=timeline_result,
        headline_result={"headline": "Test", "risk": "Low", "score": 0, "reasons": []},
        rewrite_result=rewrite_result,
        source_comparison_result={"agreement": 0, "classification": "Low Agreement", "sources_checked": 0},
    )

    score = verdict.get("score", 0)
    verdict_label = verdict.get("verdict", "N/A")
    conditions = verdict.get("conditions_met", [])

    print(f"  Score: {score}, Verdict: {verdict_label}")
    print(f"  Conditions: {conditions}")

    assert score >= 70, f"Trusted source should score >= 70, got {score}"
    manip_condition = any("manipulation" in c for c in conditions)
    assert not manip_condition, f"Unknown manipulation treated as negative: {conditions}"


run_test("Test 10: E2E verdict with Unknown signals", test_e2e_unknown)


# ===== SUMMARY =====
print("\n" + "=" * 70)
print("  VALIDATION RESULTS")
print("=" * 70)
for name, status in results:
    icon = "PASS" if status == "PASS" else "FAIL"
    print(f"  [{icon}] {name}")

print(f"\n  Total: {len(results)} tests")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
if passed + failed > 0:
    print(f"  Success rate: {passed/(passed+failed)*100:.1f}%")
print("=" * 70)

with open("validation_results.json", "w") as f:
    json.dump({
        "total": len(results), "passed": passed, "failed": failed,
        "tests": [{"name": n, "status": s} for n, s in results]
    }, f, indent=2)

sys.exit(0 if failed == 0 else 1)
