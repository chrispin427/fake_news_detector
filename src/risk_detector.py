# src/risk_detector.py

HEALTH_KEYWORDS = [
    "vaccine",
    "covid",
    "cancer",
    "doctor",
    "medicine",
    "treatment",
    "hospital",
    "health"
]

POLITICAL_KEYWORDS = [
    "election",
    "president",
    "government",
    "minister",
    "vote",
    "parliament",
    "political"
]

FINANCIAL_KEYWORDS = [
    "investment",
    "bank",
    "stock",
    "forex",
    "money",
    "loan",
    "profit"
]

SCAM_KEYWORDS = [
    "guaranteed",
    "double your money",
    "get rich",
    "crypto giveaway",
    "free bitcoin",
    "send money",
    "limited offer"
]


def detect_risk(text):

    text = text.lower()

    risks = []

    if any(word in text for word in HEALTH_KEYWORDS):
        risks.append("Health")

    if any(word in text for word in POLITICAL_KEYWORDS):
        risks.append("Political")

    if any(word in text for word in FINANCIAL_KEYWORDS):
        risks.append("Financial")

    if any(word in text for word in SCAM_KEYWORDS):
        risks.append("Scam")

    if not risks:
        risks.append("General")

    return {
        "risk_categories": risks,
        "high_risk": any(
            risk in ["Health", "Political", "Financial", "Scam"]
            for risk in risks
        )
    }