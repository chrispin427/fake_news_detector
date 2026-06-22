from urllib.parse import urlparse

# Reputation scores (0-100)
SOURCE_SCORES = {
    "reuters.com": 98,
    "apnews.com": 97,
    "bbc.com": 95,
    "bbc.co.uk": 95,
    "npr.org": 94,
    "theguardian.com": 92,
    "nytimes.com": 92,
    "washingtonpost.com": 91,

    "cnn.com": 88,
    "abcnews.go.com": 88,
    "cbsnews.com": 87,
    "nbcnews.com": 87,

    "forbes.com": 85,
    "bloomberg.com": 90,

    "foxnews.com": 80,
    "newsweek.com": 80,

    "aljazeera.com": 90,

    "dailymail.co.uk": 65,
    "the-sun.com": 60,

    "facebook.com": 40,
    "instagram.com": 40,
    "x.com": 40,
    "twitter.com": 40,
    "tiktok.com": 35,

    "youtube.com": 50,
    "youtu.be": 50
}


def get_domain(url):
    """
    Extract domain from URL.
    """

    try:
        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        domain = domain.replace("www.", "")

        return domain

    except:
        return None


def get_source_rating(url):
    """
    Return source reputation score.
    """

    domain = get_domain(url)

    if not domain:
        return {
            "domain": "Unknown",
            "score": 0,
            "label": "Unknown"
        }

    score = SOURCE_SCORES.get(domain, 50)

    if score >= 90:
        label = "Highly Trusted"
    elif score >= 75:
        label = "Trusted"
    elif score >= 60:
        label = "Mixed Reliability"
    else:
        label = "Low Reliability"

    return {
        "domain": domain,
        "score": score,
        "label": label
    }