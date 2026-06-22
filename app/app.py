import streamlit as st
import sys
import os

# Fix import path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from src.ui import apply_styles, show_header, show_footer
from src.social_media import is_url
from src.url_extractor import extract_article
from src.analyzer import analyze_article
from src.credibility import calculate_credibility_score
from src.explainer import generate_explanation
from src.source_rating import get_source_rating
from src.fact_checker import fact_check

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

apply_styles()
show_header()

st.write(
    "Paste a news article, social media claim, or article URL to verify."
)

# --------------------------------------------------
# INPUT
# --------------------------------------------------

user_input = st.text_area(
    "Paste article text or URL:",
    height=250
)

# --------------------------------------------------
# ANALYZE BUTTON
# --------------------------------------------------

if st.button("Check News"):

    if not user_input.strip():
        st.warning("⚠️ Please enter some text or URL.")
        st.stop()

    text_to_analyze = user_input

    # --------------------------------------------------
    # URL MODE
    # --------------------------------------------------

    if is_url(user_input):

        st.info("🔗 URL detected. Extracting article...")

        article = extract_article(user_input)

        if article is None:
            st.error("❌ Could not extract article.")
            st.stop()

        source_info = get_source_rating(user_input)

        st.markdown("## 📰 Article Preview")

        st.markdown(
            f"### {article['title']}"
        )

        st.text_area(
            "Extracted Content",
            article["text"][:1000],
            height=200,
            disabled=True
        )

        st.markdown("## 🏢 Source Reputation")

        st.metric(
            "Trust Score",
            f"{source_info['score']}/100"
        )

        st.info(
            f"Source: {source_info['domain']} | "
            f"{source_info['label']}"
        )

        text_to_analyze = article["text"]

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    if len(text_to_analyze.split()) < 30:

        st.warning(
            "⚠️ Please provide a FULL news article "
            "(minimum 30 words)."
        )

        st.markdown("""
        ### Example

        WASHINGTON (Reuters) - The government announced
        a new education policy today aimed at improving
        access to schools. Officials stated that the
        policy will increase funding and provide more
        resources for teachers and students nationwide.
        """)

        st.stop()

    # --------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------

    with st.spinner(
        "🔍 AI is analyzing patterns and verifying sources..."
    ):

        result = analyze_article(text_to_analyze)

        prediction = result["prediction"]
        proba = result["probabilities"]
        confidence = result["confidence"]

        results_dict = result["api_results"]
        total_results = result["total_results"]

        # Fact Check
        fact_result = fact_check(text_to_analyze)

    # --------------------------------------------------
    # AI RESULT
    # --------------------------------------------------

    st.markdown("## 🤖 AI Analysis Result")

    if confidence < 0.75:
        st.warning(
            "⚠️ Low confidence prediction. "
            "Please verify manually."
        )

    if prediction == 0:

        if total_results == 0:

            st.error(
                f"❌ Likely Fake News "
                f"({proba[0]*100:.2f}% confidence)"
            )

            st.warning(
                "No supporting evidence found "
                "from trusted sources."
            )

        else:

            st.error(
                f"⚠️ Suspicious News "
                f"({proba[0]*100:.2f}% confidence)"
            )

            st.info(
                "Related topics were found, but the "
                "article may contain misleading claims."
            )

    else:

        if total_results > 0:

            st.success(
                f"✅ Real News "
                f"({proba[1]*100:.2f}% confidence)"
            )

            st.info(
                "Verified across external sources."
            )

        else:

            st.success(
                f"✅ Likely Real News "
                f"({proba[1]*100:.2f}% confidence)"
            )

            st.warning(
                "Could not strongly verify "
                "across external sources."
            )

    # --------------------------------------------------
    # FACT CHECKER
    # --------------------------------------------------

    st.markdown("## 🔎 Fact Check")

    st.write(
        f"**Main Claim Detected:** "
        f"{fact_result['claim']}"
    )

    if fact_result["verdict"] == "Supported":
        st.success(
            "✅ Claim supported by trusted sources"
        )

    elif fact_result["verdict"] == "Partially Supported":
        st.warning(
            "⚠️ Claim partially supported"
        )

    else:
        st.error(
            "❌ Claim could not be verified"
        )

st.markdown("## 🏷️ Detected Entities")

entities = fact_result["entities"]

if entities["people"]:
    st.write(
        f"**People:** {', '.join(entities['people'])}"
    )

if entities["organizations"]:
    st.write(
        f"**Organizations:** {', '.join(entities['organizations'])}"
    )

if entities["locations"]:
    st.write(
        f"**Locations:** {', '.join(entities['locations'])}"
    )

if entities["dates"]:
    st.write(
        f"**Dates:** {', '.join(entities['dates'])}"
    )

    # --------------------------------------------------
    # CREDIBILITY SCORE
    # --------------------------------------------------

    matched_sources = sum(
        1 for value in results_dict.values()
        if value > 0
    )

    credibility_score = calculate_credibility_score(
        prediction=prediction,
        confidence=confidence,
        matched_sources=matched_sources,
        total_sources=len(results_dict)
    )

    st.markdown("## 📊 Trust Score")

    st.progress(
        credibility_score / 100
    )

    st.metric(
        label="Credibility",
        value=f"{credibility_score}/100"
    )

    # --------------------------------------------------
    # SOURCE VERIFICATION
    # --------------------------------------------------

    st.markdown("## 🌐 Source Verification")

    for api_name, count in results_dict.items():

        if count > 0:
            st.success(
                f"{api_name}: Found {count} matching articles"
            )
        else:
            st.warning(
                f"{api_name}: No matching articles found"
            )

    st.markdown(
        f"### Verification Score: "
        f"{matched_sources}/{len(results_dict)}"
    )

    # --------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------

    st.markdown(
        "## 🧠 Why did the AI make this decision?"
    )

    explanations = generate_explanation(
        prediction=prediction,
        confidence=confidence,
        matched_sources=matched_sources,
        total_sources=len(results_dict)
    )

    for item in explanations:
        st.write(f"• {item}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

show_footer()