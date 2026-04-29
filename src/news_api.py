import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWS_DATA_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")


# ---------- NEWS API ----------
def check_newsapi(query):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 3
    }

    try:
        res = requests.get(url, params=params).json()
        return res.get("totalResults", 0)
    except:
        return 0


# ---------- GNEWS ----------
def check_gnews(query):
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "apikey": GNEWS_API_KEY,
        "lang": "en",
        "max": 3
    }

    try:
        res = requests.get(url, params=params).json()
        return len(res.get("articles", []))
    except:
        return 0


# ---------- NEWSDATA ----------
def check_newsdata(query):
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": query,
        "language": "en"
    }

    try:
        res = requests.get(url, params=params).json()
        return len(res.get("results", []))
    except:
        return 0


# ---------- SERP API ----------
def check_serpapi(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
    }

    try:
        res = requests.get(url, params=params).json()
        return len(res.get("organic_results", []))
    except:
        return 0


# ---------- MASTER FUNCTION ----------
def verify_news(query):
    short_query = " ".join(query.split()[:10])

    results = {
        "NewsAPI": check_newsapi(short_query),
        "GNews": check_gnews(short_query),
        "NewsData": check_newsdata(short_query),
        "SerpApi": check_serpapi(short_query)
    }

    total = sum(results.values())

    return results, total
