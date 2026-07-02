from newspaper import Article

try:
    from src.search_fallback import search_from_failed_url
except ImportError:
    from search_fallback import search_from_failed_url


def extract_article(url):
    """
    Extract article content from a URL.

    Attempts direct extraction with newspaper3k first.  If the article
    cannot be downloaded, parsed, or contains empty content (common for
    Reuters, Facebook login walls, expired URLs, HTTP 401/403 errors,
    unsupported websites, etc.), the function falls back to a Google
    search using the URL's path keywords via `search_from_failed_url`.

    The returned object always includes:
        success (bool)
        title (str)
        text (str)
        authors (list)
        publish_date (datetime or None)
        top_image (str or None)
        url (str)
        source_type (str) -- "direct", "search_fallback", or "failed"
        fallback_results (list) -- populated only when source_type is "search_fallback"

    Never crashes or returns None.
    """

    try:
        article = Article(url)
        article.download()
        article.parse()

        text = article.text.strip()

        # Empty content means extraction failed (login wall, no JS, etc.)
        if not text:
            fallback_results = search_from_failed_url(url)
            if fallback_results:
                return {
                    "success": True,
                    "title": fallback_results[0].get("title", ""),
                    "text": fallback_results[0].get("snippet", ""),
                    "authors": [],
                    "publish_date": None,
                    "top_image": None,
                    "url": url,
                    "source_type": "search_fallback",
                    "fallback_results": fallback_results
                }
            return {
                "success": False,
                "error": "No extractable content found and search fallback returned no results.",
                "source_type": "failed"
            }

        return {
            "success": True,
            "title": article.title,
            "text": text,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "top_image": article.top_image,
            "url": url,
            "source_type": "direct"
        }

    except Exception as e:
        # Any extraction error → fall back to web search
        fallback_results = search_from_failed_url(url)
        if fallback_results:
            return {
                "success": True,
                "title": fallback_results[0].get("title", ""),
                "text": fallback_results[0].get("snippet", ""),
                "authors": [],
                "publish_date": None,
                "top_image": None,
                "url": url,
                "source_type": "search_fallback",
                "fallback_results": fallback_results
            }
        return {
            "success": False,
            "error": str(e),
            "source_type": "failed"
        }


if __name__ == "__main__":
    url = input("Enter URL: ")

    result = extract_article(url)

    if result["success"]:
        print("\nTITLE:")
        print(result["title"])

        print("\nTEXT:")
        print(result["text"][:1000])

    else:
        print("ERROR:", result["error"])