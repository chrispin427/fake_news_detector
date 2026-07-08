import os
import re
import requests
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Try to import query builder; fail gracefully if not available
_HAS_QUERY_BUILDER = False
try:
    from src.query_builder import build_queries, clean_query, format_query_summary
    _HAS_QUERY_BUILDER = True
except ImportError:
    pass


def _normalise_url(url):
    """Strip trailing slashes, protocol, and www for dedup."""
    url = url.strip().rstrip("/")
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"^www\.", "", url)
    return url.lower()


def _title_similarity(t1, t2):
    """Return 0-1 similarity between two title strings."""
    return SequenceMatcher(None, t1.lower(), t2.lower()).ratio()


def _truncate_query(query, max_chars=200):
    """Truncate a query to max_chars, breaking at a word boundary if possible."""
    if len(query) <= max_chars:
        return query
    truncated = query[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.8:
        truncated = truncated[:last_space]
    return truncated.strip()


def get_newsapi_evidence(query):
    if not NEWS_API_KEY:
        print("  [NewsAPI] API key not found")
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {"q": query, "apiKey": NEWS_API_KEY, "language": "en", "pageSize": 5, "sortBy": "relevancy"}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "error":
            print(f"  [NewsAPI] API error: {data.get('message', 'unknown')}")
            return []
        evidence = []
        for article in data.get("articles", []):
            evidence.append({"source": article.get("source", {}).get("name", "Unknown"), "title": article.get("title", ""), "url": article.get("url", "")})
        print(f"  [NewsAPI] {len(evidence)} articles returned")
        return evidence
    except Exception as e:
        print(f"  [NewsAPI] Exception: {e}")
        return []


def get_gnews_evidence(query):
    if not GNEWS_API_KEY:
        print("  [GNews] API key not found")
        return []
    safe_query = _truncate_query(query, max_chars=180)
    try:
        url = "https://gnews.io/api/v4/search"
        params = {"q": safe_query, "apikey": GNEWS_API_KEY, "lang": "en", "max": 5}
        response = requests.get(url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        if "errors" in data:
            print(f"  [GNews] API error: {data['errors']}")
            return []
        evidence = []
        for article in data.get("articles", []):
            evidence.append({"source": article.get("source", {}).get("name", "Unknown"), "title": article.get("title", ""), "url": article.get("url", "")})
        truncated_flag = len(query) != len(safe_query)
        print(f"  [GNews] {len(evidence)} articles returned (query truncated: {truncated_flag})")
        return evidence
    except Exception as e:
        print(f"  [GNews] Exception: {e}")
        return []


def get_newsdata_evidence(query):
    if not NEWSDATA_API_KEY:
        print("  [NewsData] API key not found")
        return []
    try:
        url = "https://newsdata.io/api/1/news"
        params = {"apikey": NEWSDATA_API_KEY, "q": query, "language": "en", "size": 5}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        results = data.get("results", [])
        evidence = []
        for article in results:
            evidence.append({"source": article.get("source_id", "Unknown"), "title": article.get("title", ""), "url": article.get("link", "")})
        print(f"  [NewsData] {len(evidence)} articles returned")
        return evidence
    except Exception as e:
        print(f"  [NewsData] Exception: {e}")
        return []


def get_serpapi_evidence(query):
    if not SERP_API_KEY:
        print("  [SerpAPI] API key not found")
        return []
    try:
        url = "https://serpapi.com/search.json"
        params = {"engine": "google_news", "q": query, "api_key": SERP_API_KEY}
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        news_results = data.get("news_results", [])
        evidence = []
        seen_urls = set()
        for item in news_results:
            link = item.get("link") or item.get("url", "")
            if not link or link in seen_urls:
                continue
            seen_urls.add(link)
            evidence.append({"source": item.get("source", "Google News"), "title": item.get("title", ""), "url": link})
        print(f"  [SerpAPI] {len(evidence)} articles returned")
        return evidence
    except Exception as e:
        print(f"  [SerpAPI] Exception: {e}")
        return []


def _query_one_api(api_fn, api_name, query):
    """Query a single API and log the request query."""
    print(f"  [{api_name}] Query: {query[:120]}")
    try:
        return api_fn(query)
    except Exception as e:
        print(f"  [{api_name}] Unexpected error in _query_one_api: {e}")
        return []


def _query_all_apis(query):
    """Query all 4 APIs with a single query and return combined results with per-API counts."""
    sources = {}
    newsapi = _query_one_api(get_newsapi_evidence, "NewsAPI", query)
    sources["NewsAPI"] = len(newsapi)
    gnews = _query_one_api(get_gnews_evidence, "GNews", query)
    sources["GNews"] = len(gnews)
    newsdata = _query_one_api(get_newsdata_evidence, "NewsData", query)
    sources["NewsData"] = len(newsdata)
    serpapi = _query_one_api(get_serpapi_evidence, "SerpAPI", query)
    sources["SerpAPI"] = len(serpapi)

    combined = newsapi + gnews + newsdata + serpapi
    return combined, sources


def _deduplicate(combined):
    """Deduplicate combined evidence list by URL and title similarity."""
    total = len(combined)
    unique = []
    seen_urls = set()
    seen_titles = []

    for item in combined:
        url = item.get("url", "")
        title = item.get("title", "")
        normalised_url = _normalise_url(url) if url else ""
        if normalised_url and normalised_url in seen_urls:
            continue
        if title:
            is_dup = False
            for existing_title, _ in seen_titles:
                if _title_similarity(title, existing_title) > 0.85:
                    is_dup = True
                    break
            if is_dup:
                continue
        if normalised_url:
            seen_urls.add(normalised_url)
        seen_titles.append((title, True))
        unique.append(item)

    return unique, total - len(unique)


def find_evidence(query):
    """
    Collect evidence using multiple query strategies.

    The single query string is treated as the primary search term and
    passed through query_builder to generate multiple query variants
    (title, claim, keywords, URL slug, entities). Each variant is tried
    against all 4 APIs and results are merged into a single deduplicated pool.

    This is the main entry point used by app.py, debug_audit.py, and
    other callers. For advanced usage with explicit title/claim/url/text,
    call find_evidence_multi() directly.
    """
    sep_line = "=" * 60
    print("")
    print(sep_line)
    print(f"  EVIDENCE FINDER - Query: {query[:100]}")
    print(sep_line)

    # Try multi-query strategy using the query as the primary title
    if _HAS_QUERY_BUILDER:
        queries = build_queries(title=query, claim=query)
        if queries:
            print(f"\n  --- Query Strategy ---")
            for i, q in enumerate(queries, 1):
                print(f"    {i}. [{q['variant']}] {q['query'][:100]}")

            all_evidence = []
            for qv in queries:
                variant = qv["variant"]
                query_text = qv["query"]
                print(f"\n  >> Trying [{variant}]: {query_text[:80]}")
                combined, sources = _query_all_apis(query_text)
                if combined:
                    print(f"  << [{variant}] returned {len(combined)} raw results")
                    all_evidence.extend(combined)
                else:
                    print(f"  << [{variant}] returned 0 results")

            print(f"\n  --- Multi-merge ---")
            print(f"    Total raw across variants: {len(all_evidence)}")
            unique, dups = _deduplicate(all_evidence)
            print(f"    Duplicates removed:  {dups}")
            print(f"    Final evidence count: {len(unique)}")
            print(sep_line)
            return unique[:15]

    # Fallback: single-query approach
    print("  Falling back to single-query strategy")
    combined, sources = _query_all_apis(query)
    print(f"\n  --- Per-API summary ---")
    for name, count in sorted(sources.items()):
        print(f"    {name}: {count} articles")
    print(f"    Total before dedup: {len(combined)}")
    unique, dups = _deduplicate(combined)
    print(f"    Duplicates removed:  {dups}")
    print(f"    Final evidence count: {len(unique)}")
    print(sep_line)
    return unique[:10]


def find_evidence_multi(title=None, claim=None, url=None, text=None, entities=None):
    """
    Collect evidence using multiple query strategies.

    Uses src.query_builder to generate query variants in priority order:
      1. Cleaned article title
      2. Extracted claim
      3. Keyword-only title (5-8 words)
      4. URL slug query
      5. Keyword-only claim
      6. Entity-based query
      7. First 12 words of text (fallback)

    Each variant is tried against all 4 APIs. Results are merged into a
    single deduplicated evidence pool. Logs detailed per-API and per-query stats.
    """
    sep_line = "=" * 60
    print("")
    print(sep_line)
    print("  EVIDENCE FINDER - Multi-query strategy")
    print(sep_line)

    if _HAS_QUERY_BUILDER:
        queries = build_queries(title=title, claim=claim, url=url, text=text, entities=entities)
    else:
        # Fallback: just use the first available input
        fallback = title or claim or text or ""
        if url and not fallback:
            from urllib.parse import urlparse
            fallback = urlparse(url).path.replace("-", " ").replace("/", " ")
        queries = [{"variant": "fallback", "query": fallback[:200], "source": "fallback"}] if fallback else []

    if not queries:
        print("  [EvidenceFinder] No queries could be generated.")
        return []

    # Log query summary
    print(f"\n  --- Query Strategy ---")
    for i, q in enumerate(queries, 1):
        print(f"    {i}. [{q['variant']}] {q['query'][:100]}")

    # Try each query variant; accumulate all evidence
    all_evidence = []
    seen_variant_results = set()  # tracks (variant, api_name) to avoid logging duplicates

    for qv in queries:
        variant = qv["variant"]
        query_text = qv["query"]
        print(f"\n  >> Trying query variant [{variant}]: {query_text[:80]}")

        combined, sources = _query_all_apis(query_text)

        if combined:
            print(f"  << Variant [{variant}] returned {len(combined)} raw results")
            all_evidence.extend(combined)
        else:
            print(f"  << Variant [{variant}] returned 0 results - trying next variant")

    # Deduplicate across all variants
    print(f"\n  --- Multi-query dedup ---")
    print(f"    Total raw evidence across all variants: {len(all_evidence)}")

    unique, dups = _deduplicate(all_evidence)

    print(f"    Duplicates removed:  {dups}")
    print(f"    Final evidence count: {len(unique)}")

    # Per-variant breakdown
    print(f"\n  --- Query Variants Used ---")
    for i, q in enumerate(queries, 1):
        print(f"    {i}. [{q['variant']}] ({q['source']})")

    print(sep_line)
    return unique[:15]
