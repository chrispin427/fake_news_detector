import pickle

from src.preprocess import clean_text
from src.news_api import verify_news


# Load once when app starts
model = pickle.load(
    open("model/model.pkl", "rb")
)

vectorizer = pickle.load(
    open("model/vectorizer.pkl", "rb")
)


def analyze_article(text):

    cleaned = clean_text(text)

    vectorized = vectorizer.transform(
        [cleaned]
    )

    prediction = model.predict(
        vectorized
    )[0]

    probabilities = model.predict_proba(
        vectorized
    )[0]

    confidence = max(probabilities)

    query = " ".join(
        text.split()[:10]
    )

    api_results, total_results = verify_news(
        query
    )

    return {
        "prediction": prediction,
        "probabilities": probabilities,
        "confidence": confidence,
        "api_results": api_results,
        "total_results": total_results
    }