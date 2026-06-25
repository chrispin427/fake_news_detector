import streamlit as st
import sys
import os

# Fix import path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from src.ui import apply_styles, render_hero, render_sidebar, show_footer, render_section_header, render_verdict_card, render_status_badge, render_evidence_card, render_download_section
from src.social_media import is_url
from src.url_extractor import extract_article
from src.analyzer import analyze_article
from src.credibility import calculate_credibility_score
from src.explainer import generate_explanation
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

        st.write("\u2714\ufe0f **Calculating credibility score...**")
        try:
            matched_sources = sum(1 for v in results_dict.values() if v > 0) if results_dict else 0
            total_sources = len(results_dict) if results_dict else 0
            credibility_score = calculate_credibility_score(prediction=prediction, confidence=confidence, matched_sources=matched_sources, total_sources=total_sources if total_sources > 0 else 1)
        except Exception as e:
            st.warning("Credibility scoring failed: " + str(e))
            credibility_score = 0
            matched_sources = 0
            total_sources = 0

        st.write("\u2714\ufe0f **Generating explanation...**")
        try:
            explanations = generate_explanation(prediction=prediction, confidence=confidence, matched_sources=matched_sources, total_sources=total_sources if total_sources > 0 else 1)
        except Exception as e:
            st.warning("Explanation generation failed: " + str(e))
            explanations = ["Explanation could not be generated."]

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
            verdict_result = generate_verdict(prediction=prediction, confidence=confidence, credibility_score=credibility_score, matched_sources=matched_sources, total_sources=total_sources if total_sources > 0 else 1, sentiment_result=sentiment_result, risk_result=adapted_risk, timeline_result=adapted_timeline, headline_result=headline_result, rewrite_result=rewrite_result, source_comparison_result=source_comparison_result)
        except Exception as e:
            st.warning("Verdict generation failed: " + str(e))
            verdict_result = {"score": credibility_score, "verdict": "Uncertain"}

        st.write("\u2714\ufe0f **Building report...**")
        report = None
        report_text = ""
        try:
            report = generate_report(article_title=article_title, verdict_result=verdict_result, credibility_score=credibility_score, source_info=source_info, fact_result=fact_result, timeline_result=adapted_timeline, sentiment_result=sentiment_result, virality_result=virality_result, risk_result=adapted_risk, source_comparison_result=source_comparison_result, evidence=evidence, headline_result=headline_result, rewrite_result=rewrite_result)
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
    # DASHBOARD METRICS ROW
    # ============================================================

    st.markdown("---")
    verdict_score = verdict_result.get("score", credibility_score)

    dash_cols = st.columns(5)
    with dash_cols[0]:
        st.metric(label="Credibility", value=str(credibility_score) + "/100", help="Overall credibility score")
    with dash_cols[1]:
        st.metric(label="Trust Score", value=str(source_info.get("score", 0)) + "/100", help="Source reputation")
    with dash_cols[2]:
        st.metric(label="Consensus", value=str(source_comparison_result.get("agreement", 0)) + "%", help="Source agreement")
    with dash_cols[3]:
        manip_risk = rewrite_result.get("risk", "High")
        manip_display = "Low" if manip_risk == "Low" else ("Med" if manip_risk == "Medium" else "High")
        st.metric(label="Manipulation", value=manip_display, help="Content manipulation risk")
    with dash_cols[4]:
        viral_level = virality_result.get("level", "Low")
        st.metric(label="Virality", value=viral_level, help="How widely shared")

    st.markdown("---")

    # ============================================================
    # A. EXECUTIVE SUMMARY
    # ============================================================

    render_section_header("\U0001f4cb", "Executive Summary")

    verdict_label = verdict_result.get("verdict", "Uncertain")
    if verdict_label in ("Highly Credible", "Likely Credible"):
        explanation_text = "Verified across trusted sources with strong evidence support." if total_results > 0 else "Classified as credible based on ML analysis."
    elif verdict_label == "Uncertain":
        explanation_text = "Insufficient evidence to make a strong determination."
    else:
        explanation_text = "Contains unsupported claims and weak source verification."

    render_verdict_card(verdict_label, verdict_score, explanation_text)

    for item in explanations:
        st.write("\u2022 " + item)

    st.markdown(f'<div style="margin-top:8px;"><strong>Confidence:</strong> {confidence*100:.1f}%</div>', unsafe_allow_html=True)
    st.progress(confidence)

    # ============================================================
    # B. SOURCE ANALYSIS
    # ============================================================

    render_section_header("\U0001f310", "Source Analysis")
    render_section_header("\U0001f3e2", "Source Reputation")
    src_cols = st.columns(3)
    with src_cols[0]:
        st.metric("Domain", source_info.get("domain", "N/A"))
    with src_cols[1]:
        st.metric("Trust Score", str(source_info.get("score", 0)) + "/100")
    with src_cols[2]:
        render_status_badge(source_info.get("label", "N/A"), "blue")

    render_section_header("\U0001f517", "Source Verification")
    if results_dict:
        sv_col1, sv_col2 = st.columns([3, 1])
        with sv_col2:
            st.metric("Matched", str(matched_sources) + "/" + str(total_sources))
        for api_name, count in results_dict.items():
            if count > 0:
                st.success("**" + api_name + ":** Found " + str(count) + " matching articles")
            else:
                st.warning("**" + api_name + ":** No matching articles found")
    else:
        st.info("No source verification data available (API keys may be missing).")

    render_section_header("\U0001f91d", "Source Consensus")
    agmt = source_comparison_result.get("agreement", 0)
    classification = source_comparison_result.get("classification", "N/A")
    sources_checked = source_comparison_result.get("sources_checked", 0)
    sc_cols = st.columns(3)
    with sc_cols[0]:
        st.metric("Agreement", str(agmt) + "%")
    with sc_cols[1]:
        cls_color = "green" if classification == "High Agreement" else ("yellow" if classification == "Moderate Agreement" else "red")
        render_status_badge(classification, cls_color)
    with sc_cols[2]:
        st.metric("Sources", sources_checked)

    # ============================================================
    # C. FACT CHECKING
    # ============================================================

    render_section_header("\U0001f50e", "Fact Checking")

    render_section_header("\U0001f4a1", "Detected Claim")
    if claim_text:
        st.info("**" + claim_text + "**")
    else:
        st.info("No claim could be extracted from the text.")

    render_section_header("\u2696\ufe0f", "Fact Check Verdict")
    fact_verdict = fact_result.get("verdict", "Unverified")
    fact_color = "green" if fact_verdict == "Supported" else ("yellow" if fact_verdict == "Partially Supported" else "red")
    render_status_badge(fact_verdict, fact_color)
    st.write("**Sources matched:** " + str(fact_result.get("sources", 0)))

    render_section_header("\U0001f3f7\ufe0f", "Detected Entities")
    if any(entities.values()):
        en_cols = st.columns(4)
        with en_cols[0]:
            st.metric("People", len(entities.get("people", [])))
            if entities.get("people"):
                st.caption(", ".join(entities["people"][:5]))
        with en_cols[1]:
            st.metric("Organizations", len(entities.get("organizations", [])))
            if entities.get("organizations"):
                st.caption(", ".join(entities["organizations"][:5]))
        with en_cols[2]:
            st.metric("Locations", len(entities.get("locations", [])))
            if entities.get("locations"):
                st.caption(", ".join(entities["locations"][:5]))
        with en_cols[3]:
            st.metric("Dates", len(entities.get("dates", [])))
            if entities.get("dates"):
                st.caption(", ".join(entities["dates"][:5]))
    else:
        st.info("No named entities detected in the text.")

    render_section_header("\U0001f4da", "Supporting Evidence")
    if evidence:
        for item in evidence[:10]:
            render_evidence_card(item.get("title", "Untitled"), item.get("source", "Unknown"), item.get("url", ""))
    else:
        st.info("No supporting evidence found from external sources.")

    # ============================================================
    # D. MANIPULATION ANALYSIS
    # ============================================================

    render_section_header("\u26a0\ufe0f", "Manipulation Analysis")

    render_section_header("\U0001f4f0", "Headline Analysis")
    hl_score = headline_result.get("score", 0)
    hl_risk = headline_result.get("risk", "Low")
    hl_reasons = headline_result.get("reasons", [])
    hl_cols = st.columns(2)
    with hl_cols[0]:
        hl_color = "green" if hl_risk == "Low" else ("yellow" if hl_risk == "Medium" else "red")
        render_status_badge(hl_risk + " Risk", hl_color)
    with hl_cols[1]:
        st.metric("Sensationalism Score", str(hl_score) + "/100")
    if hl_reasons:
        for reason in hl_reasons:
            st.write("\u2022 " + reason)
    else:
        st.info("No sensationalism or clickbait indicators detected.")

    render_section_header("\u270f\ufe0f", "Content Manipulation")
    rw_similarity = rewrite_result.get("similarity", 0)
    rw_risk = rewrite_result.get("risk", "High")
    rw_explanation = rewrite_result.get("explanation", "")
    rw_cols = st.columns(2)
    with rw_cols[0]:
        st.metric("Source Similarity", str(rw_similarity) + "%")
    with rw_cols[1]:
        rw_color = "green" if rw_risk == "Low" else ("yellow" if rw_risk == "Medium" else "red")
        render_status_badge(rw_risk + " Risk", rw_color)
    if rw_explanation:
        st.info(rw_explanation)

    render_section_header("\U0001f4ac", "Sentiment Analysis")
    sent_cols = st.columns(3)
    with sent_cols[0]:
        polarity = sentiment_result.get("polarity", 0)
        polarity_label = "Positive" if polarity > 0.1 else ("Negative" if polarity < -0.1 else "Neutral")
        st.metric("Polarity", "{:.2f}".format(polarity) + " (" + polarity_label + ")")
    with sent_cols[1]:
        man_risk = sentiment_result.get("manipulation_risk", "Low")
        man_color = "green" if man_risk == "Low" else ("yellow" if man_risk == "Medium" else "red")
        render_status_badge(man_risk + " Risk", man_color)
    with sent_cols[2]:
        words = sentiment_result.get("sensational_words", [])
        st.metric("Sensational Words", len(words))
    if words:
        st.write("**Detected:** " + ", ".join(words))

    render_section_header("\U0001f4d0", "Claim-Article Similarity")
    sim_cols = st.columns(2)
    with sim_cols[0]:
        st.metric("Similarity Score", str(similarity_score) + "%")
    with sim_cols[1]:
        if similarity_score > 80:
            st.success("Strong alignment between claim and article")
        elif similarity_score > 50:
            st.info("Moderate alignment between claim and article")
        else:
            st.warning("Weak alignment - claim may not match article content")

    # ============================================================
    # E. CONTEXT ANALYSIS
    # ============================================================

    render_section_header("\U0001f4ca", "Context Analysis")

    render_section_header("\u26a0\ufe0f", "Risk Assessment")
    risk_categories = risk_result.get("risk_categories", ["General"])
    st.write("**Categories:** " + ", ".join(risk_categories))
    if risk_result.get("high_risk", False):
        st.error("High Risk - involves sensitive topics (Health, Political, Financial, or Scam)")
    else:
        st.success("Low Risk - general content")

    render_section_header("\U0001f4c8", "Virality Analysis")
    vir_cols = st.columns(2)
    with vir_cols[0]:
        st.metric("Total Mentions", virality_result.get("mentions", 0))
    with vir_cols[1]:
        spread_level = virality_result.get("level", "Low")
        spread_color = "green" if spread_level in ("Low",) else ("yellow" if spread_level == "Medium" else "red")
        render_status_badge(spread_level, spread_color)

    render_section_header("\U0001f4c5", "Timeline Analysis")
    tl_status = timeline_result.get("status", "Unknown")
    tl_years = timeline_result.get("years_old")
    tl_cols = st.columns(2)
    with tl_cols[0]:
        st.metric("Status", tl_status)
    with tl_cols[1]:
        if tl_years is not None:
            st.metric("Age", str(tl_years) + " years")
        else:
            st.metric("Age", "Unknown")
    if tl_status == "Old Article":
        st.warning("This article is older than 1 year. Context may have changed.")
    elif tl_status == "Recent":
        st.success("This article is recent.")
    elif tl_status == "Not Recent":
        st.info("This article is from the past few months.")

    # ============================================================
    # F. FULL REPORT
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