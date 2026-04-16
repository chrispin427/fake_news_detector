import pickle
from preprocess import clean_text

# Load model and vectorizer
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

def predict_news(text):
    # Clean input
    cleaned_text = clean_text(text)
    
    # Convert to vector
    vectorized_text = vectorizer.transform([cleaned_text])
    
    # Predict
    prediction = model.predict(vectorized_text)[0]
    
    # Return result
    if prediction == 0:
        return "Fake News ❌"
    else:
        return "Real News ✅"
    
if __name__ == "__main__":
    sample = input("Enter news text: ")
    result = predict_news(sample)
    print("Prediction:", result)