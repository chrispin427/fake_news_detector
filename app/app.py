import streamlit as st
import pickle
import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocess import clean_text
from src.ui import apply_styles, show_header, show_footer
from src.news_api import check_news_api

# Apply styles
apply_styles()

# Show header
show_header()

# Load model and vectorizer
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

# App title
st.title("📰 DETECT FAKE NEWS WITH Ai")

st.write("Enter a news headline or article to check if it's real or fake.")

# Input box
user_input = st.text_area("Enter news text here:")

# Button
if st.button("Check News"):
    if user_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        # Clean text
        cleaned = clean_text(user_input)

        # Vectorize
        vectorized = vectorizer.transform([cleaned])

        # Predict
        prediction = model.predict(vectorized)[0]

        # Output result
        results = check_news_api(user_input)

        if results > 0:
           st.info("📰 This topic is reported by trusted news sources")
        else:
           st.warning("⚠️ No matching news found from trusted sources")
show_footer()            