import os
import re
import requests

from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")


# --------------------------------------------------
# GOOGLE SEARCH VIA SERPAPI
# --------------------------------------------------

def search_web(query, num_results=10):
    """
    Search Google using SerpAPI.
    """

    if not SERP_API_KEY:
        print("SERP_API_KEY not found in .env")
        return []

    try:

        url = "https://serpapi.com/search.json"

        params = {
            "engine": "google",
            "q": query,
            "api_key": SERP_API_KEY,
            "num": num_results
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get(
            "organic_results",
            []
        ):

            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })

        return results

    except Exception as e:

        print(
            "Search Fallback Error:",
            e
        )

        return []


# --------------------------------------------------
# URL -> SEARCH QUERY
# --------------------------------------------------

def extract_keywords_from_url(url):
    """
    Convert article URL into a search query.
    """

    try:

        path = urlparse(url).path

        path = path.replace("-", " ")
        path = path.replace("_", " ")
        path = path.replace("/", " ")

        # Remove file extensions
        path = path.replace(".html", "")
        path = path.replace(".htm", "")

        # Remove long IDs/numbers
        path = re.sub(
            r"\b\d+\b",
            "",
            path
        )

        # Collapse spaces
        path = re.sub(
            r"\s+",
            " ",
            path
        )

        query = path.strip()

        if not query:
            return url

        return query

    except Exception:

        return url


# --------------------------------------------------
# SEARCH FROM FAILED URL
# --------------------------------------------------

def search_from_failed_url(url):
    """
    If article extraction fails,
    search using URL keywords.
    """

    query = extract_keywords_from_url(
        url
    )

    return search_web(query)


# --------------------------------------------------
# BEST MATCH
# --------------------------------------------------

def get_best_search_result(url):
    """
    Return the top Google result
    for a failed article URL.
    """

    results = search_from_failed_url(
        url
    )

    if len(results) == 0:
        return None

    return results[0]