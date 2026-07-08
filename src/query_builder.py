"""
src/query_builder.py

Generates optimised, multi-variant search queries for evidence retrieval.
Responsible for:
  - Cleaning queries (stopwords, punctuation, duplicate words)
  - Extracting keywords (top N important words)
  - Parsing URL slugs into search queries
  - Generating multiple query variants from a single article

Usage:
    from src.query_builder import build_queries
    for q in build_queries(title=..., claim=..., url=..., text=..., entities=...):
        print(q["variant"], q["query"])
"""

import re

_STOPWORDS = frozenset({
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
    "yet", "about", "up", "down", "over", "under", "between", "among",
    "through", "during", "before", "after", "above", "below", "against",
    "within", "without", "across", "behind", "along", "toward", "via",
    "per", "until", "since", "upon", "versus",
    "get", "got", "gets", "make", "made", "makes", "take", "took",
    "takes", "see", "seen", "saw", "know", "known", "knew", "knows",
    "like", "look", "looks", "looked", "going", "go", "went", "gone",
    "come", "came", "comes", "think", "thinks", "thought",
    "would", "could", "should", "might", "must",
    "one", "two", "first", "last", "next", "previous",
    "also", "even", "still", "already", "yet",
})


def _remove_punctuation(text):
    """Strip punctuation while keeping internal hyphens and apostrophes."""
    cleaned = re.sub(r"[^\w\s\u2019\u2018-]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _tokenise(text):
    """Split text into tokens, preserving contractions like don't and it's."""
    return [t for t in re.findall(r"[a-zA-Z0-9]+(?:'[a-zA-Z0-9]+)?", text) if len(t) > 0]


def _remove_stopwords(tokens):
    """Filter out stopwords."""
    return [t for t in tokens if t.lower() not in _STOPWORDS]


def _deduplicate_tokens(tokens):
    """Remove duplicate tokens while preserving order."""
    seen = set()
    result = []
    for t in tokens:
        lower = t.lower()
        if lower not in seen:
            seen.add(lower)
            result.append(t)
    return result


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def clean_query(query):
    """
    Clean a search query by removing punctuation, stopwords, and duplicate words.
    Also strips common news prefixes and publisher tags so the query is
    focused on the substantive content.
    """
    if not query:
        return ""

    # Strip HTML entities
    cleaned = query.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    cleaned = cleaned.replace("&#039;", "'").replace("&quot;", '"')

    # Remove news prefixes (BREAKING, EXCLUSIVE, etc.)
    cleaned = re.sub(r"^(BREAKING|EXCLUSIVE|UPDATE|LIVE|URGENT|JUST IN)\s*[:-]\s*", "", cleaned, flags=re.IGNORECASE)

    # Remove publisher tags (BBC:, Reuters:, etc.)
    cleaned = re.sub(r"^(BBC|BBC News|Reuters|AP|Associated Press|Financial Times|WSJ|The Guardian|NPR)\s*[:-]\s*", "", cleaned, flags=re.IGNORECASE)

    # Remove trailing site names ( - BBC News)
    cleaned = re.sub(r"\s*[-|]\s*(BBC|BBC News|Reuters|AP News|The Guardian|NPR|YouTube|WSJ)$", "", cleaned, flags=re.IGNORECASE)

    # Remove consecutive duplicate words
    cleaned = re.sub(r"\b(\w+)\s+\1\b", r"\1", cleaned, flags=re.IGNORECASE)

    cleaned = _remove_punctuation(cleaned)
    tokens = _tokenise(cleaned)
    tokens = _remove_stopwords(tokens)
    tokens = _deduplicate_tokens(tokens)

    return " ".join(tokens)


def extract_keywords(query, max_words=8):
    """
    Extract the top N most important keywords from a query.
    Prefers capitalised words (proper nouns) and longer words.
    Returns a string of max_words or fewer keywords.
    """
    if not query:
        return ""

    tokens = _tokenise(query)
    tokens = [t for t in tokens if len(t) > 2]
    tokens = _deduplicate_tokens(tokens)

    scored = []
    for t in tokens:
        score = 0.0
        if t[0].isupper():
            score += 3.0
        if t.isupper() and len(t) <= 5:
            score += 2.0
        score += min(len(t) / 5.0, 2.0)
        scored.append((score, t))

    scored.sort(reverse=True, key=lambda x: x[0])
    keywords = [t for _, t in scored]
    if len(keywords) > max_words:
        keywords = keywords[:max_words]

    return " ".join(keywords)


def extract_keywords_from_url(url):
    """
    Convert an article URL path into a search query.
    Handles BBC, Reuters, AP, and general URL formats.
    """
    if not url:
        return ""

    from urllib.parse import urlparse, unquote

    try:
        parsed = urlparse(url)
        path = unquote(parsed.path)

        # Replace separators with spaces
        path = path.replace("-", " ").replace("_", " ").replace("/", " ")

        # Remove file extensions
        path = re.sub(r"\.(html?|php|asp|aspx|jsp)$", "", path, flags=re.IGNORECASE)

        # Remove numeric IDs, dates (e.g. 2024-01-15, /1234567)
        path = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", path)
        path = re.sub(r"\b\d{5,}\b", "", path)

        # Remove URL noise
        path = re.sub(r"\b(www|http|https|com|org|net|html|php)\b", "", path, flags=re.IGNORECASE)

        # Collapse spaces
        path = re.sub(r"\s+", " ", path).strip()

        if not path or len(path) < 3:
            return ""

        return path
    except Exception:
        return ""


def extract_entities_query(entities):
    """
    Build a search query from extracted named entities.
    Entities dict should have keys: people, organizations, locations, dates.
    """
    if not entities:
        return ""

    parts = []
    for key in ("organizations", "people", "locations"):
        items = entities.get(key, [])
        for item in items:
            if isinstance(item, str) and item.strip():
                parts.append(item.strip())

    # Deduplicate
    seen = set()
    unique = []
    for p in parts:
        lower = p.lower()
        if lower not in seen:
            seen.add(lower)
            unique.append(p)

    return " ".join(unique[:10])


def build_queries(title=None, claim=None, url=None, text=None, entities=None):
    """
    Generate multiple search-ready query variants from available inputs.

    Priority order:
        1. Cleaned article title       (best match for finding related coverage)
        2. Extracted claim
        3. Keyword-only title           (5-8 important words)
        4. URL slug query
        5. Keyword-only claim
        6. Entity-based query
        7. First 12 words of article text  (fallback)

    Returns list of dicts, each with:
        - variant (str): label describing the query type
        - query (str): the cleaned search query
        - source (str): where the query was derived from
    """
    queries = []

    # --- 1. Cleaned article title ---
    if title:
        cleaned_title = clean_query(title)
        if cleaned_title and len(cleaned_title) >= 5:
            queries.append({"variant": "title", "query": cleaned_title, "source": "article title"})

    # --- 2. Extracted claim ---
    if claim:
        cleaned_claim = clean_query(claim)
        if cleaned_claim and len(cleaned_claim) >= 5:
            existing = [q["query"].lower() for q in queries]
            if cleaned_claim.lower() not in existing:
                queries.append({"variant": "claim", "query": cleaned_claim, "source": "extracted claim"})

    # --- 3. Keyword-only version of the title ---
    if title:
        kw_title = extract_keywords(title, max_words=8)
        if kw_title and len(kw_title) >= 5:
            existing = [q["query"].lower() for q in queries]
            if kw_title.lower() not in existing:
                queries.append({"variant": "keywords_title", "query": kw_title, "source": "title keywords"})

    # --- 4. URL slug query ---
    if url:
        url_query = extract_keywords_from_url(url)
        if url_query and len(url_query) >= 5:
            url_keywords = extract_keywords(url_query, max_words=8)
            if url_keywords and len(url_keywords) >= 5:
                queries.append({"variant": "url_slug", "query": url_keywords, "source": "URL slug"})

    # --- 5. Keyword-only version of the claim ---
    if claim:
        kw_claim = extract_keywords(claim, max_words=8)
        if kw_claim and len(kw_claim) >= 5:
            existing = [q["query"].lower() for q in queries]
            if kw_claim.lower() not in existing:
                queries.append({"variant": "keywords_claim", "query": kw_claim, "source": "claim keywords"})

    # --- 6. Entity-based query ---
    if entities:
        entity_query = extract_entities_query(entities)
        if entity_query and len(entity_query) >= 5:
            queries.append({"variant": "entities", "query": entity_query, "source": "extracted entities"})

    # --- 7. Fallback: first 12 words of text ---
    if text and not queries:
        first_words = " ".join(text.split()[:12])
        cleaned_fallback = clean_query(first_words)
        if cleaned_fallback and len(cleaned_fallback) >= 5:
            queries.append({"variant": "fallback", "query": cleaned_fallback, "source": "article text (first 12 words)"})

    # Log
    if queries:
        print(f"\n  [QueryBuilder] Generated {len(queries)} query variant(s):")
        for i, q in enumerate(queries, 1):
            print(f"    {i}. [{q['variant']}] ({q['source']}): {q['query'][:120]}")
    else:
        print("  [QueryBuilder] No queries could be generated from available inputs")

    return queries


def format_query_summary(queries):
    """Return a human-readable summary of the generated queries."""
    lines = ["QUERY SUMMARY", "-" * 60]
    for i, q in enumerate(queries, 1):
        lines.append(f"  Query {i}: [{q['variant']}]")
        lines.append(f"           Source: {q['source']}")
        lines.append(f"           Text:   {q['query'][:140]}")
        lines.append("")
    return "\n".join(lines)
