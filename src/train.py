import pandas as pd
from preprocess import clean_text
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle

# -----------------------------
# 1. Load datasets
# -----------------------------
fake = pd.read_csv("data/Fake.csv", sep="\t", encoding="latin1")
true = pd.read_csv("data/True.csv", sep="\t", encoding="latin1")

# -----------------------------
# 2. Select relevant columns
# -----------------------------
fake = fake[["title", "text"]]
true = true[["title", "text"]]

# -----------------------------
# 3. Add labels
# -----------------------------
fake["label"] = 0
true["label"] = 1

# -----------------------------
# 4. Combine datasets
# -----------------------------
data = pd.concat([fake, true], axis=0)

# Shuffle
data = data.sample(frac=1).reset_index(drop=True)

# Remove missing values
data = data.dropna()

print(data.head())
print("\nDataset shape:", data.shape)

# -----------------------------
# 5. Create content column
# -----------------------------
data["content"] = data["title"] + " " + data["text"]

# Clean text
data["content"] = data["content"].apply(clean_text)

print(data[["content", "label"]].head())

# -----------------------------
# 6. Split data
# -----------------------------
X = data["content"]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------
# 7. TF-IDF Vectorization
# -----------------------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_df=0.7,
    ngram_range=(1,2),   # 👈 THIS IS IMPORTANT
    max_features=10000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# -----------------------------
# 8. Train model
# -----------------------------
model = LogisticRegression(max_iter=1000)

model.fit(X_train_tfidf, y_train)

# -----------------------------
# 9. Evaluate model
# -----------------------------
y_pred = model.predict(X_test_tfidf)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# -----------------------------
# 10. Save model
# -----------------------------
pickle.dump(model, open("model/model.pkl", "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))