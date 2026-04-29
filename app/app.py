import streamlit as st
import pickle
import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocess import clean_text
from src.ui import apply_styles, show_header, show_footer
from src.news_api import verify_news   # ✅ NEW IMPORT

# Apply styles
apply_styles()

# Show header
show_header()

st.write("Enter a full news article to check if it's real or fake.")

# Load model and vectorizer
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

# Input box
user_input = st.text_area("Paste full news article here:")

# Button
if st.button("Check News"):

    #  Empty input
    if user_input.strip() == "":
        st.warning("⚠️ Please enter some text.")

    #  Too short
    elif len(user_input.split()) < 30:
        st.warning("⚠️ Please provide a FULL news article (minimum 30 words).")

        st.markdown("""
        ### 📄 Example of valid input:

        *WASHINGTON (Reuters) - The government announced a new education policy today aimed at improving access to schools. Officials stated that the policy will increase funding and provide more resources for teachers and students nationwide.*
        """)
        st.stop()

    # ✅ Valid input
    else:
        with st.spinner(" AI is analyzing patterns and verifying sources..."):

            # Clean text
            cleaned = clean_text(user_input)

            # Vectorize
            vectorized = vectorizer.transform([cleaned])

            # Predict
            prediction = model.predict(vectorized)[0]
            proba = model.predict_proba(vectorized)[0]
            confidence = max(proba)

            #  MULTI-API VERIFICATION
            results_dict, total_results = verify_news(user_input)

            #  AI RESULT
            st.markdown("###  AI Analysis Result")

            #  Uncertainty
            if confidence < 0.75:
                st.warning(" Uncertain result — please verify manually.")

            #  FAKE
            if prediction == 0:
                if total_results == 0:
                    st.error(f" Likely Fake News ({proba[0]*100:.2f}% confidence)")
                else:
                    st.error(f" Suspicious News ({proba[0]*100:.2f}% confidence)")
                    st.info(" Some related topics exist, but content may be misleading")

            # ✅ REAL
            elif prediction == 1:
                if total_results > 0:
                    st.success(f" Real News ({proba[1]*100:.2f}% confidence)")
                    st.info(" Verified across multiple sources")
                else:
                    st.success(f" Likely Real News ({proba[1]*100:.2f}% confidence)")
                    st.warning(" Could not strongly verify across sources")

            # 🌐 SHOW EACH API RESULT
            st.markdown("### 🌐 Source Verification")

            for api, count in results_dict.items():
                if count > 0:
                    st.success(f" {api}: Found {count} related articles")
                else:
                    st.warning(f" {api}: No matching articles found")

            # 📊 Verification Score
            matched_sources = sum(1 for v in results_dict.values() if v > 0)
            total_sources = len(results_dict)

            st.markdown(f"###  Verification Score: {matched_sources}/{total_sources} sources matched")

# Footer
show_footer()
