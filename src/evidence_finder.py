import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")


# -----------------------------------
# NEWS API
# -----------------------------------

def get_newsapi_evidence(query):

    if not NEWS_API_KEY:
        print("❌ NEWS_API_KEY not found")
        return []

    try:

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "language": "en",
            "pageSize": 5,
            "sortBy": "relevancy"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if data.get("status") == "error":
            print("NewsAPI Error:", data)
            return []

        evidence = []

        for article in data.get("articles", []):

            evidence.append({
                "source": article.get(
                    "source",
                    {}
                ).get(
                    "name",
                    "Unknown"
                ),
                "title": article.get(
                    "title",
                    ""
                ),
                "url": article.get(
                    "url",
                    ""
                )
            })

        return evidence

    except Exception as e:

        print("NewsAPI Error:", e)

        return []


# -----------------------------------
# GNEWS
# -----------------------------------

def get_gnews_evidence(query):

    if not GNEWS_API_KEY:
        print("❌ GNEWS_API_KEY not found")
        return []

    try:

        url = "https://gnews.io/api/v4/search"

        params = {
            "q": query,
            "apikey": GNEWS_API_KEY,
            "lang": "en",
            "max": 5
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        data = response.json()

        if "errors" in data:
            print("GNews Error:", data)
            return []

        evidence = []

        for article in data.get("articles", []):

            evidence.append({
                "source": article.get(
                    "source",
                    {}
                ).get(
                    "name",
                    "Unknown"
                ),
                "title": article.get(
                    "title",
                    ""
                ),
                "url": article.get(
                    "url",
                    ""
                )
            })

        return evidence

    except Exception as e:

        print("GNews Error:", e)

        return []


# -----------------------------------
# MASTER FUNCTION
# -----------------------------------

def find_evidence(query):

    evidence = []

    evidence.extend(
        get_newsapi_evidence(query)
    )

    evidence.extend(
        get_gnews_evidence(query)
    )

    # Remove duplicates
    seen = set()
    unique = []

    for item in evidence:

        key = item["url"]

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:10]