import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWS_DATA_API_KEY = os.getenv("NEWS_DATA_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

TEST_QUERY = "Donald Trump news"


def test_newsapi():
    print("\n Testing NewsAPI...")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": TEST_QUERY,
        "apiKey": NEWS_API_KEY,
        "pageSize": 1
    }

    try:
        res = requests.get(url, params=params).json()
        if res.get("status") == "ok":
            print(" NewsAPI working")
        else:
            print(" NewsAPI error:", res)
    except Exception as e:
        print(" NewsAPI failed:", e)


def test_gnews():
    print("\n Testing GNews...")
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": TEST_QUERY,
        "apikey": GNEWS_API_KEY,
        "max": 1
    }

    try:
        res = requests.get(url, params=params).json()
        if "articles" in res:
            print(" GNews working")
        else:
            print(" GNews error:", res)
    except Exception as e:
        print(" GNews failed:", e)


def test_newsdata():
    print("\n Testing NewsData...")
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWS_DATA_API_KEY,
        "q": TEST_QUERY
    }

    try:
        res = requests.get(url, params=params).json()
        if "results" in res:
            print(" NewsData working")
        else:
            print(" NewsData error:", res)
    except Exception as e:
        print(" NewsData failed:", e)


def test_serpapi():
    print("\n Testing SerpApi...")
    url = "https://serpapi.com/search"
    params = {
        "q": TEST_QUERY,
        "api_key": SERP_API_KEY
    }

    try:
        res = requests.get(url, params=params).json()
        if "organic_results" in res:
            print(" SerpApi working")
        else:
            print(" SerpApi error:", res)
    except Exception as e:
        print(" SerpApi failed:", e)


if __name__ == "__main__":
    print(" RUNNING LIVE API TESTS...")

    test_newsapi()
    test_gnews()
    test_newsdata()
    test_serpapi()