import pickle
import sys
import os

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocess import clean_text

# Load model
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

def predict_news(text):
    cleaned_text = clean_text(text)
    vectorized_text = vectorizer.transform([cleaned_text])

    prediction = model.predict(vectorized_text)[0]
    proba = model.predict_proba(vectorized_text)[0]

    return prediction, proba

# Run in terminal
if __name__ == "__main__":
    sample = input("Enter news article: ")
    prediction, proba = predict_news(sample)

    if prediction == 0:
        print(f"Fake News ({proba[0]*100:.2f}%)")
    else:
        print(f"Real News ({proba[1]*100:.2f}%)")
