"""
src/test_queries.py

Diagnostic tool for the evidence retrieval layer.

Usage:
    python src/test_queries.py "https://www.bbc.com/news/articles/..."
    python src/test_queries.py "UK Parliament votes on new trade deal"
    python src/test_queries.py --file input.txt
"""

import sys
import os

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def diagnose_text(text):
    """Run diagnostics on a text input."""
    _print_header("TEXT INPUT DIAGNOSTIC")
    print(f"  Input:      {text[:150]}")
    print(f"  Word count: {len(text.split())}")

    HAS_QB = False
    try:
        from src.query_builder import build_queries, clean_query, extract_keywords, extract_entities_query, format_query_summary
        HAS_QB = True
    except ImportError:
        print("  [WARN] query_builder not available")

    entity_q = ""
    all_queries = []

    if HAS_QB:
        cleaned = clean_query(text)
        print(f"\n  ORIGINAL:   {text[:120]}")
        print(f"  CLEANED:    {cleaned[:120]}")
        keywords = extract_keywords(text, max_words=8)
        print(f"  KEYWORDS:   {keywords[:120]}")
        try:
            from src.claim_extractor import extract_claim
            claim_t = extract_claim(text)
        except ImportError:
            claim_t = text[:300]
        cleaned_claim = clean_query(claim_t)
        print(f"  CLAIM:      {cleaned_claim[:120]}")
        try:
            from src.entity_extractor import extract_entities
            entities = extract_entities(text)
            entity_q = extract_entities_query(entities)
            print(f"  ENTITIES:   {entity_q[:120]}")
        except ImportError:
            entities = None
        all_queries = build_queries(title=text[:200], claim=claim_t, text=text, entities=entities)
        print(f"\n  {format_query_summary(all_queries)}")

    print(f"\n{'='*60}")
    print("  EVIDENCE RETRIEVAL")
    print(f"{'='*60}")
    try:
        from src.evidence_finder import find_evidence_multi
        evidence = find_evidence_multi(title=text[:200], claim=claim_t if HAS_QB else text[:300], text=text)
        print(f"\n  Total evidence: {len(evidence)}")
        if evidence:
            print(f"\n  --- Evidence list ---")
            for i, item in enumerate(evidence[:10], 1):
                s = item.get("source", "?")
                t = item.get("title", "")[:100]
                print(f"    {i}. [{s}] {t}")
        else:
            print("  No evidence found.")
    except Exception as e:
        import traceback
        print(f"  ERROR: {e}")
        traceback.print_exc()
    print(f"\n{'='*60}")
    print("  DIAGNOSTIC COMPLETE")
    print(f"{'='*60}")


def diagnose_url(url):
    _print_header("URL DIAGNOSTIC")
    print(f"  URL: {url}")
    from urllib.parse import urlparse
    print(f"  Domain: {urlparse(url).netloc}")
    try:
        from src.source_rating import get_source_rating
        r = get_source_rating(url)
        print(f"  Source: {r.get('domain','?')} | Score: {r.get('score',0)}")
    except ImportError:
        pass
    try:
        from src.url_extractor import extract_article
        article = extract_article(url)
        if not article.get("success", False):
            print(f"  Extraction failed: {article.get('error','?')}")
            return
        title = article.get("title", "Untitled")
        text = article.get("text", "")
        print(f"  Title: {title}")
        print(f"  Text: {len(text.split())} words")
    except Exception as e:
        print(f"  Extraction error: {e}")
        return

    try:
        from src.query_builder import build_queries, clean_query, extract_keywords_from_url, format_query_summary
        from src.claim_extractor import extract_claim
        from src.entity_extractor import extract_entities
        cleaned = clean_query(title)
        print(f"\n  TITLE CLEANED: {cleaned[:120]}")
        claim_t = extract_claim(text)
        entities = extract_entities(text)
        all_q = build_queries(title=title, claim=claim_t, url=url, text=text, entities=entities)
        print(f"\n  {format_query_summary(all_q)}")
    except ImportError:
        all_q = []

    print(f"\n{'='*60}")
    print("  EVIDENCE RETRIEVAL")
    print(f"{'='*60}")
    try:
        from src.evidence_finder import find_evidence_multi
        evidence = find_evidence_multi(title=title, claim=claim_t if 'claim_t' in dir() else text[:300], url=url, text=text)
        print(f"\n  Total evidence: {len(evidence)}")
        if evidence:
            for i, item in enumerate(evidence[:10], 1):
                s = item.get("source", "?")
                t = item.get("title", "")[:100]
                u = item.get("url", "")[:60]
                print(f"    {i}. [{s}] {t}")
                print(f"        {u}")
        else:
            print("  No evidence found.")
    except Exception as e:
        import traceback
        print(f"  ERROR: {e}")
        traceback.print_exc()
    print(f"\n{'='*60}")
    print("  DIAGNOSTIC COMPLETE")
    print(f"{'='*60}")


def _print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--file" and len(sys.argv) > 2:
            with open(sys.argv[2], "r", encoding="utf-8") as f:
                text = f.read()
            if text.strip().startswith(("http://", "https://")):
                diagnose_url(text.strip())
            else:
                diagnose_text(text)
        else:
            arg = " ".join(sys.argv[1:])
            if arg.startswith(("http://", "https://")):
                diagnose_url(arg)
            else:
                diagnose_text(arg)
    else:
        print(f"{'='*60}")
        print("  QUERY DIAGNOSTIC TOOL")
        print(f"{'='*60}")
        user_input = input("Enter URL or article text: ").strip()
        if user_input.startswith(("http://", "https://")):
            diagnose_url(user_input)
        else:
            diagnose_text(user_input)
