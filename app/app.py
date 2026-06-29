import streamlit as st
import sys
import os

# Fix import path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from src.ui import (
    apply_styles, render_hero, render_sidebar, show_footer,
    render_section_header, render_status_badge,
    render_verdict_card, render_verdict_metrics, render_why_this_verdict,
    render_evidence_section, render_advanced_analysis_section,
    render_fact_check_result, render_entity_metrics,
    render_source_verification, render_technical_metrics,
    render_sentiment_analysis, render_virality_analysis,
    render_timeline_analysis, render_risk_analysis,
    render_source_comparison, render_headline_analysis,
    render_rewrite_analysis, render_similarity_analysis,
    render_download_section
)
from src.social_media import is_url
from src.url_extractor import extract_article
from src.analyzer import analyze_article
from src.source_rating import get_source_rating
from src.fact_checker import fact_check
from src.social_preview import get_preview
from src.entity_extractor import extract_entities
from src.evidence_finder import find_evidence
from src.similarity_checker import calculate_similarity
from src.sentiment_analyzer import analyze_sentiment
from src.virality_detector import calculate_virality
from src.risk_detector import detect_risk
from src.timeline_checker import check_timeline
from src.verdict_engine import generate_verdict
from src.report_generator import generate_report, generate_report_text, generate_pdf
from src.source_comparison import compare_sources
from src.headline_checker import analyze_headline
from src.rewrite_detector import detect_rewrite

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

apply_styles()
render_sidebar()
render_hero()

user_input = st.text_area(
    "Paste a news article, social media claim, or URL here...",
    height=220,
    placeholder="Paste a news article, social media claim, or URL here..."
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_clicked = st.button("\U0001f50d Analyze Article", type="primary")

if analyze_clicked:

    if not user_input.strip():
        st.warning("Please enter some text or URL to analyze.")
        st.stop()

    text_to_analyze = user_input
    article_title = "User-Submitted Text"

    # --------------------------------------------------
    # URL MODE
    # --------------------------------------------------

    publish_date = None
    source_info = {"domain": "N/A", "score": 0, "label": "N/A"}

    if is_url(user_input):
        with st.status("Extracting article from URL...", expanded=True) as url_status:
            st.info("URL detected. Extracting article...")
            article_result = extract_article(user_input)
            if not article_result.get("success", False):
                st.error("Could not extract article: " + article_result.get("error", "Unknown error"))
                st.stop()
            text_to_analyze = article_result["text"]
            article_title = article_result.get("title", "Untitled Article")
            publish_date = article_result.get("publish_date")
            try:
                preview = get_preview(user_input)
            except Exception:
                preview = None
            render_section_header("\U0001f4f0", "Article Preview")
            st.markdown("### " + article_title)
            if preview and preview.get("image"):
                st.image(preview["image"], use_container_width=True)
            if preview and preview.get("description"):
                st.info(preview["description"])
            st.text_area("Extracted Content", text_to_analyze[:1500], height=200, disabled=True)
            if article_result.get("authors"):
                st.write("**Authors:** " + ", ".join(article_result["authors"]))
            if publish_date:
                st.write("**Published:** " + str(publish_date))
            render_section_header("\U0001f3e2", "Source Reputation")
            source_info = get_source_rating(user_input)
            sr_col1, sr_col2 = st.columns([1, 2])
            with sr_col1:
                st.metric("Trust Score", str(source_info["score"]) + "/100")
            with sr_col2:
                render_status_badge(source_info["label"], "blue")
                st.write("**Domain:** " + source_info["domain"])
            url_status.update(label="Article extracted successfully", state="complete")

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    if len(text_to_analyze.split()) < 30:

        st.warning("Please provide a FULL news article (minimum 30 words).")

        st.markdown("""
        ### Example

        WASHINGTON (Reuters) - The government announced
        a new education policy today aimed at improving
        access to schools. Officials stated that the
        policy will increase funding and provide more
        resources for teachers and students nationwide.
        """)

        st.stop()

    # ============================================================
    # ANALYSIS PIPELINE
    # ============================================================

    with st.status("\U0001f50d Analyzing article...", expanded=True) as analysis_status:
        st.write("\u2714\ufe0f **Running ML prediction model...**")
        try:
            result = analyze_article(text_to_analyze)
            prediction = result["prediction"]
            probabilities = result["probabilities"]
            confidence = result["confidence"]
            results_dict = result["api_results"]
            total_results = result["total_results"]
        except Exception as e:
            st.error("ML analysis failed: " + str(e))
            prediction = 0
            probabilities = [0.5, 0.5]
            confidence = 0.5
            results_dict = {}
            total_results = 0

        st.write("\u2714\ufe0f **Running fact check...**")
        try:
            fact_result = fact_check(text_to_analyze)
            claim_text = fact_result["claim"]
        except Exception as e:
            st.warning("Fact check failed: " + str(e))
            fact_result = {"claim": "Could not extract claim", "verdict": "Unverified", "sources": 0, "results": {}, "entities": {"people": [], "organizations": [], "locations": [], "dates": []}}
            claim_text = ""

        st.write("\u2714\ufe0f **Extracting entities...**")
        try:
            entities = extract_entities(text_to_analyze)
        except Exception as e:
            st.warning("Entity extraction failed: " + str(e))
            entities = {"people": [], "organizations": [], "locations": [], "dates": []}

        st.write("\u2714\ufe0f **Gathering supporting evidence...**")
        try:
            evidence_query = claim_text if claim_text else " ".join(text_to_analyze.split()[:10])
            evidence = find_evidence(evidence_query)
            st.write("Found " + str(len(evidence)) + " evidence items")
        except Exception as e:
            st.warning("Evidence gathering failed: " + str(e))
            evidence = []

        st.write("\u2714\ufe0f **Running similarity analysis...**")
        try:
            similarity_score = calculate_similarity(claim_text, text_to_analyze) if claim_text else 0
        except Exception as e:
            st.warning("Similarity analysis failed: " + str(e))
            similarity_score = 0

        st.write("\u2714\ufe0f **Analyzing sentiment...**")
        try:
            sentiment_result = analyze_sentiment(text_to_analyze)
        except Exception as e:
            st.warning("Sentiment analysis failed: " + str(e))
            sentiment_result = {"polarity": 0, "sensational_words": [], "manipulation_risk": "Low"}

        st.write("\u2714\ufe0f **Detecting virality signals...**")
        try:
            virality_result = calculate_virality(results_dict)
        except Exception as e:
            st.warning("Virality detection failed: " + str(e))
            virality_result = {"mentions": 0, "level": "Low"}

        st.write("\u2714\ufe0f **Analyzing risk factors...**")
        try:
            risk_result = detect_risk(text_to_analyze)
        except Exception as e:
            st.warning("Risk detection failed: " + str(e))
            risk_result = {"risk_categories": ["General"], "high_risk": False}

        st.write("\u2714\ufe0f **Analyzing timeline...**")
        try:
            timeline_result = check_timeline(publish_date)
        except Exception as e:
            st.warning("Timeline analysis failed: " + str(e))
            timeline_result = {"status": "Unknown", "years_old": None}

        st.write("\u2714\ufe0f **Calculating source verification metrics...**")
        try:
            matched_sources = sum(1 for v in results_dict.values() if v > 0) if results_dict else 0
            total_sources = len(results_dict) if results_dict else 0
        except Exception as e:
            st.warning("Source metrics calculation failed: " + str(e))
            matched_sources = 0
            total_sources = 0

        st.write("\u2714\ufe0f **Running source comparison...**")
        try:
            source_comparison_result = compare_sources(claim_text, evidence)
        except Exception as e:
            st.warning("Source comparison failed: " + str(e))
            source_comparison_result = {"agreement": 0, "classification": "Low Agreement", "sources_checked": 0}

        st.write("\u2714\ufe0f **Analyzing headline...**")
        try:
            headline_result = analyze_headline(article_title)
        except Exception as e:
            st.warning("Headline analysis failed: " + str(e))
            headline_result = {"headline": article_title, "risk": "Low", "score": 0, "reasons": []}

        st.write("\u2714\ufe0f **Detecting content manipulation...**")
        try:
            rewrite_result = detect_rewrite(claim_text, evidence)
        except Exception as e:
            st.warning("Content manipulation detection failed: " + str(e))
            rewrite_result = {"similarity": 0.0, "risk": "High", "explanation": "Analysis failed."}

        st.write("\u2714\ufe0f **Generating final verdict...**")
        adapted_risk = {**risk_result, "risk_level": risk_result.get("risk_level", "Low")}
        adapted_timeline = {**timeline_result, "is_old_news": (timeline_result.get("status") == "Old Article")}
        try:
            risk_level = "High" if risk_result.get("high_risk") else ("Medium" if len(risk_result.get("risk_categories", [])) > 1 else "Low")
            adapted_risk = {**risk_result, "risk_level": risk_level}
            adapted_timeline = {**timeline_result, "is_old_news": (timeline_result.get("status") == "Old Article")}
            verdict_result = generate_verdict(
                source_info=source_info,
                prediction=prediction,
                confidence=confidence,
                matched_sources=matched_sources,
                total_sources=total_sources if total_sources > 0 else 1,
                fact_result=fact_result,
                evidence=evidence,
                sentiment_result=sentiment_result,
                risk_result=adapted_risk,
                timeline_result=adapted_timeline,
                headline_result=headline_result,
                rewrite_result=rewrite_result,
                source_comparison_result=source_comparison_result
            )
        except Exception as e:
            st.warning("Verdict generation failed: " + str(e))
            verdict_result = {"score": 50, "verdict": "Mixed Evidence", "explanations": ["Verdict engine error occurred."]}

        st.write("\u2714\ufe0f **Building report...**")
        report = None
        report_text = ""
        try:
            report = generate_report(article_title=article_title, verdict_result=verdict_result, credibility_score=verdict_result.get("score", 50), source_info=source_info, fact_result=fact_result, timeline_result=adapted_timeline, sentiment_result=sentiment_result, virality_result=virality_result, risk_result=adapted_risk, source_comparison_result=source_comparison_result, evidence=evidence, headline_result=headline_result, rewrite_result=rewrite_result)
            report_text = generate_report_text(report)
        except Exception as e:
            st.warning("Report generation failed: " + str(e))

        pdf_bytes = None
        try:
            if report:
                pdf_bytes = generate_pdf(report)
        except ImportError:
            st.warning("PDF generation requires reportlab.")
        except Exception as e:
            st.warning("PDF generation failed: " + str(e))

        analysis_status.update(label="\u2705 Analysis complete!", state="complete")

    # ============================================================
    # 1. VERDICT CARD (prominent, top of results)
    # ============================================================

    st.markdown("---")
    verdict_score = verdict_result.get("score", 50)
    verdict_label = verdict_result.get("verdict", "Mixed Evidence")
    verdict_explanations = verdict_result.get("explanations", [])
    explanation_text = verdict_explanations[0] if verdict_explanations else "Analysis complete."

    # Large verdict card
    render_verdict_card(verdict_label, verdict_score, explanation_text)

    # Trust Score + Confidence side by side
    trust_score = source_info.get("score", 0)
    render_verdict_metrics(trust_score, confidence, source_info.get("label", "N/A"))

    # ============================================================
    # 2. WHY THIS VERDICT?
    # ============================================================

    render_why_this_verdict(verdict_explanations)

    # ============================================================
    # 3. SUPPORTING EVIDENCE
    # ============================================================

    render_evidence_section(evidence)

    # ============================================================
    # 4. ADVANCED ANALYSIS (collapsible - hidden by default)
    # ============================================================

    with render_advanced_analysis_section():

        # --- Source Reputation ---
        st.markdown("**\U0001f3e2 Source Reputation**")
        src_cols = st.columns(3)
        with src_cols[0]:
            st.metric("Domain", source_info.get("domain", "N/A"))
        with src_cols[1]:
            st.metric("Trust Score", str(source_info.get("score", 0)) + "/100")
        with src_cols[2]:
            label = source_info.get("label", "N/A")
            label_colors = {"Highly Trusted": "green", "Trusted": "green", "Mixed Reliability": "yellow", "Low Reliability": "red", "Unknown": "blue"}
            lc = label_colors.get(label, "blue")
            c_map = {"green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171", "blue": "#60a5fa"}
            st.markdown(f'<span style="display:inline-block;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:600;text-transform:uppercase;background:rgba(59,130,246,0.15);color:{c_map.get(lc, "#60a5fa")};">{label}</span>', unsafe_allow_html=True)

        # --- Fact Check ---
        st.markdown("---")
        st.markdown("**\u2696\ufe0f Fact Check**")
        fact_verdict = fact_result.get("verdict", "Unverified")
        fact_sources = fact_result.get("sources", 0)
        render_fact_check_result(claim_text, fact_verdict, fact_sources)

        # --- Entity Detection ---
        st.markdown("**\U0001f3f7\ufe0f Entity Detection**")
        render_entity_metrics(entities)

        # --- Source Verification ---
        st.markdown("**\U0001f517 Source Verification**")
        render_source_verification(results_dict, matched_sources, total_sources)

        # --- Source Consensus ---
        st.markdown("**\U0001f91d Source Consensus**")
        render_source_comparison(source_comparison_result)

        # --- Headline Analysis ---
        st.markdown("**\U0001f4f0 Headline Analysis**")
        render_headline_analysis(headline_result)

        # --- Content Manipulation ---
        st.markdown("**\u270f\ufe0f Content Manipulation**")
        render_rewrite_analysis(rewrite_result)

        # --- Sentiment Analysis ---
        st.markdown("**\U0001f4ac Sentiment Analysis**")
        render_sentiment_analysis(sentiment_result)

        # --- Similarity Analysis ---
        st.markdown("**\U0001f4d0 Claim-Article Similarity**")
        render_similarity_analysis(similarity_score)

        # --- Timeline Analysis ---
        st.markdown("**\U0001f4c5 Timeline Analysis**")
        render_timeline_analysis(timeline_result)

        # --- Risk Assessment ---
        st.markdown("**\u26a0\ufe0f Risk Assessment**")
        render_risk_analysis(risk_result)

        # --- Virality Analysis ---
        st.markdown("**\U0001f4c8 Virality Analysis**")
        render_virality_analysis(virality_result)

        # --- Score Breakdown ---
        st.markdown("**\U0001f4ca Score Breakdown**")
        render_technical_metrics(verdict_result.get("breakdown", {}))

    # ============================================================
    # 5. DOWNLOAD REPORT
    # ============================================================

    st.markdown("---")
    render_download_section()

    dl_cols = st.columns(2)
    with dl_cols[0]:
        if report_text:
            st.download_button(label="\U0001f4c4 Download TXT Report", data=report_text, file_name="fake_news_report.txt", mime="text/plain", use_container_width=True)
    with dl_cols[1]:
        if pdf_bytes:
            st.download_button(label="\U0001f4d5 Download PDF Report", data=pdf_bytes, file_name="fake_news_report.pdf", mime="application/pdf", use_container_width=True)

    if report_text and not pdf_bytes:
        with st.expander("\U0001f4c4 View Full Report"):
            st.text(report_text)

show_footer()