import pandas as pd
from preprocess import clean_text
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle

# ✅ Load CLEAN dataset
data = pd.read_csv("data/cleaned_data.csv")

# Combine title + text
data["content"] = data["title"] + " " + data["text"]

# Clean text
data["content"] = data["content"].apply(clean_text)

X = data["content"]
y = data["label"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Vectorize
vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Evaluate
y_pred = model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy*100)

# Save model
pickle.dump(model, open("model/model.pkl", "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))
