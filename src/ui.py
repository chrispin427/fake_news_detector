# src/ui.py
import streamlit as st


def apply_styles():
    st.set_page_config(page_title="AI Fact Checker", page_icon="🔍", layout="centered")
    st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#070b15 0%,#0f1529 40%,#141b2d 100%);color:#e2e8f0;}
h1,h2,h3,h4,h5,h6{color:#f1f5f9!important;font-weight:600!important;}
p,li,.stMarkdown,.stText{color:#cbd5e1!important;}
.stTextArea textarea{background:#1a2236!important;border:1px solid #2a3456!important;border-radius:14px!important;padding:16px!important;color:#e2e8f0!important;}
.stButton>button{background:linear-gradient(135deg,#22c55e,#16a34a)!important;color:white!important;border-radius:12px!important;height:3.2em!important;font-weight:600!important;box-shadow:0 4px 14px rgba(34,197,94,0.25)!important;transition:all 0.2s ease!important;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(34,197,94,0.35)!important;}
.stMetric{background:#1a2236;border:1px solid #2a3456;border-radius:12px;padding:16px;}
.stMetric label{color:#94a3b8!important;font-size:13px!important;font-weight:500!important;text-transform:uppercase;}
.stMetric [data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:28px!important;font-weight:700!important;}
.stProgress>div>div{background-color:#22c55e!important;border-radius:8px;}
.stProgress>div{background-color:#2a3456!important;border-radius:8px;height:8px!important;}
.streamlit-expanderHeader{background:#1a2236!important;border:1px solid #2a3456!important;border-radius:10px!important;color:#e2e8f0!important;font-weight:600!important;}
.streamlit-expanderHeader:hover{border-color:#3b82f6!important;}
.stAlert{border-radius:10px!important;}
hr{border:none!important;height:1px!important;background:linear-gradient(90deg,transparent,#2a3456,transparent)!important;}
[data-testid="stSidebar"]{background:#0f1529!important;border-right:1px solid #1e293b!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] li{color:#94a3b8!important;font-size:13px!important;}
.block-container{padding-top:24px!important;}
.evidence-card{background:#1a2236;border:1px solid #2a3456;border-radius:10px;padding:14px 16px;margin:8px 0;transition:border-color 0.2s ease;}
.evidence-card:hover{border-color:#3b82f6;}
</style>""", unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div style="text-align:center;padding:32px 20px 16px;">
        <div style="display:inline-block;background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);border-radius:20px;padding:4px 14px;font-size:12px;color:#4ade80;font-weight:500;text-transform:uppercase;margin-bottom:16px;">
            AI-Powered Analysis
        </div>
        <h1 style="font-size:2.6rem;font-weight:800;background:linear-gradient(135deg,#f1f5f9,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;">
            AI Fact Checker
        </h1>
        <p style="font-size:16px;color:#94a3b8;max-width:600px;margin:0 auto;line-height:1.6;">
            Verify articles, social media posts, and news claims using machine learning, source verification, and evidence analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:8px 0;">
            <h1 style="font-size:22px;font-weight:800;background:linear-gradient(135deg,#f1f5f9,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px;">
                🔍 AI Fact Checker
            </h1>
            <p style="font-size:12px;color:#64748b;">v2.0</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("AI Fact Checker uses ML and multi-source verification to detect misinformation and assess credibility.")
        st.markdown("### ⚙️ How Analysis Works")
        st.markdown("""
        1. **Source Verification** - Evaluates domain reputation
        2. **Fact Check** - Cross-references claims
        3. **Evidence** - Collects supporting articles
        4. **Multi-dimensional** - Sentiment, virality, risk, timeline, headline, and manipulation
        5. **ML** - Text pattern analysis (supporting signal)
        """)
        st.markdown("---")
        st.markdown('<p style="text-align:center;color:#64748b;font-size:12px;">AI Fact Checker v2.0</p>', unsafe_allow_html=True)


def render_section_header(icon, title):
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin:24px 0 12px;"><div style="font-size:20px;width:36px;height:36px;display:flex;align-items:center;justify-content:center;background:rgba(59,130,246,0.1);border-radius:10px;">{icon}</div><div style="font-size:18px!important;font-weight:600!important;color:#f1f5f9!important;margin:0!important;">{title}</div></div>', unsafe_allow_html=True)


def render_status_badge(label, level):
    colors = {"green":("rgba(34,197,94,0.15)","#4ade80"),"yellow":("rgba(245,158,11,0.15)","#fbbf24"),"red":("rgba(239,68,68,0.15)","#f87171"),"blue":("rgba(59,130,246,0.15)","#60a5fa")}
    bg, text = colors.get(level, colors["blue"])
    st.markdown(f'<span style="display:inline-block;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:600;text-transform:uppercase;background:{bg};color:{text};">{label}</span>', unsafe_allow_html=True)


def show_footer():
    st.markdown("---")
    st.markdown('<div style="text-align:center;padding:8px 0;"><p style="color:#64748b;font-size:12px;margin:0;">🔍 AI Fact Checker &bull; For informational purposes only.</p></div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# VERDICT CARD
# ------------------------------------------------------------------

def _get_verdict_theme(verdict):
    """Return (border_color, text_color, bg_gradient, accent, shadow) for a verdict."""
    themes = {
        "Highly Credible": ("#22c55e", "#4ade80", "linear-gradient(135deg,#0a1f12,#0d2818)", "rgba(34,197,94,0.15)", "0 0 40px rgba(34,197,94,0.12)"),
        "Likely Credible": ("#86efac", "#a7f3d0", "linear-gradient(135deg,#0a1f12,#0f1f15)", "rgba(134,239,172,0.1)", "0 0 30px rgba(134,239,172,0.08)"),
        "Mixed Evidence": ("#fbbf24", "#fcd34d", "linear-gradient(135deg,#1a1808,#1f1a0a)", "rgba(251,191,36,0.1)", "0 0 30px rgba(251,191,36,0.07)"),
        "Suspicious": ("#fb923c", "#fdba74", "linear-gradient(135deg,#1a0f08,#1f1208)", "rgba(251,146,60,0.1)", "0 0 30px rgba(251,146,60,0.08)"),
        "Highly Suspicious": ("#ef4444", "#f87171", "linear-gradient(135deg,#1a0808,#1f0a0a)", "rgba(239,68,68,0.1)", "0 0 30px rgba(239,68,68,0.1)")
    }
    return themes.get(verdict, themes["Mixed Evidence"])


def render_verdict_card(verdict, score, explanation):
    """Render a large, prominent verdict card at the top of results."""
    border, color, bg, accent, shadow = _get_verdict_theme(verdict)

    st.markdown(f"""
    <div style="background:{bg};border:2px solid {border};border-radius:20px;padding:36px 40px;text-align:center;margin:8px 0 24px;box-shadow:{shadow};">
        <div style="display:inline-block;background:{accent};border-radius:12px;padding:4px 16px;font-size:12px;font-weight:600;text-transform:uppercase;color:{color};margin-bottom:12px;letter-spacing:0.5px;">
            Final Verdict
        </div>
        <div style="font-size:36px;font-weight:800;color:{color};margin-bottom:8px;letter-spacing:-0.5px;">
            {verdict}
        </div>
        <div style="font-size:56px;font-weight:800;color:{color};margin-bottom:4px;letter-spacing:-1px;">
            {score}/100
        </div>
        <div style="font-size:14px;color:#94a3b8;max-width:500px;margin:8px auto 0;line-height:1.5;">
            {explanation}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_verdict_metrics(trust_score, confidence, source_label):
    """Render trust score and confidence metrics next to each other."""
    trust_col, conf_col = st.columns(2)
    with trust_col:
        st.metric(label="Trust Score", value=str(trust_score) + "/100", help="Source reputation score")
    with conf_col:
        st.metric(label="Confidence", value="{:.0f}%".format(confidence * 100), help="Overall analysis confidence")


# ------------------------------------------------------------------
# WHY THIS VERDICT?
# ------------------------------------------------------------------

def render_why_this_verdict(explanations):
    """Render only contributing findings from the verdict engine."""
    st.markdown("### 📋 Why This Verdict?")

    # The verdict engine already only generates explanations that contributed
    # to the verdict. We only filter out generic fallback messages.
    skip_exact = ["Analysis complete.", ""]
    important = [e for e in explanations if e not in skip_exact]
    
    if not important:
        st.info("No specific factors were flagged beyond the overall analysis.")
        return

    for item in important:
        # Determine icon based on content
        if "trusted" in item.lower() or "published by" in item.lower() or "credible" in item.lower():
            icon = "✅"
        elif "agreement" in item.lower():
            icon = "🤝"
        elif "supported" in item.lower() or "evidence" in item.lower() or "articles" in item.lower():
            icon = "📰"
        elif "strong" in item.lower() or "across" in item.lower():
            icon = "🛡️"
        elif "override" in item.lower() or "insufficient" in item.lower():
            icon = "⚖️"
        elif "reputation" in item.lower():
            icon = "🏛️"
        elif "manipulation" in item.lower() or "rewrite" in item.lower() or "misinformation" in item.lower():
            icon = "⚠️"
        elif "clickbait" in item.lower() or "sensationalism" in item.lower() or "headline" in item.lower():
            icon = "📢"
        elif "fake" in item.lower() or "suspicious" in item.lower():
            icon = "🚩"
        elif "confidence" in item.lower():
            icon = "📊"
        elif "weak" in item.lower() or "low" in item.lower() or "fewer" in item.lower():
            icon = "❌"
        elif "multiple signals" in item.lower():
            icon = "🔴"
        else:
            icon = "•"

        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:10px;padding:6px 0;">
            <span style="font-size:16px;flex-shrink:0;margin-top:1px;">{icon}</span>
            <span style="font-size:14px;color:#cbd5e1;line-height:1.5;">{item}</span>
        </div>
        """, unsafe_allow_html=True)


# ------------------------------------------------------------------
# SUPPORTING EVIDENCE
# ------------------------------------------------------------------

def render_evidence_section(evidence):
    """Render supporting evidence as clean cards with source, headline, link."""
    st.markdown("### 📰 Supporting Evidence")

    if not evidence:
        st.info("No supporting evidence found from external sources.")
        return

    st.markdown(f"Found **{len(evidence)}** external articles related to this claim.")
    
    for item in evidence[:10]:
        title = item.get("title", "Untitled")
        source = item.get("source", "Unknown")
        url = item.get("url", "")

        url_html = ""
        if url:
            # Truncate long URLs for display
            display_url = url if len(url) < 60 else url[:57] + "..."
            url_html = f'<div style="margin-top:4px;"><a href="{url}" target="_blank" style="font-size:12px;color:#3b82f6;text-decoration:none;word-break:break-all;">🔗 {display_url}</a></div>'

        st.markdown(f"""
        <div class="evidence-card">
            <div style="font-size:14px;font-weight:600;color:#e2e8f0;">{title}</div>
            <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
                <span style="font-size:12px;color:#22c55e;font-weight:500;">📰 {source}</span>
            </div>
            {url_html}
        </div>
        """, unsafe_allow_html=True)


# ------------------------------------------------------------------
# ADVANCED ANALYSIS (collapsible)
# ------------------------------------------------------------------

def render_advanced_analysis_section():
    """Render the collapsible Advanced Analysis container start."""
    return st.expander("🔬 Advanced Analysis", expanded=False)


def render_fact_check_result(claim_text, fact_verdict, fact_sources):
    """Render fact check result inside Advanced Analysis."""
    col1, col2 = st.columns([3, 1])
    with col1:
        if claim_text:
            st.info("**" + claim_text + "**")
        else:
            st.info("No claim could be extracted from the text.")
    with col2:
        fact_color = "green" if fact_verdict == "Supported" else ("yellow" if fact_verdict == "Partially Supported" else "red")
        colors_map = {"green": ("rgba(34,197,94,0.15)", "#4ade80"), "yellow": ("rgba(245,158,11,0.15)", "#fbbf24"), "red": ("rgba(239,68,68,0.15)", "#f87171")}
        bg, c = colors_map.get(fact_color, colors_map["red"])
        st.markdown(f'<span style="display:inline-block;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:600;text-transform:uppercase;background:{bg};color:{c};">{fact_verdict}</span>', unsafe_allow_html=True)
        st.caption(f"{fact_sources} sources matched")


def render_entity_metrics(entities):
    """Render entity detection in Advanced Analysis."""
    if any(entities.values()):
        en_cols = st.columns(4)
        with en_cols[0]:
            st.metric("People", len(entities.get("people", [])))
            if entities.get("people"):
                st.caption(", ".join(entities["people"][:5]))
        with en_cols[1]:
            st.metric("Orgs", len(entities.get("organizations", [])))
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
        st.info("No named entities detected.")


def render_source_verification(results_dict, matched_sources, total_sources):
    """Render source verification results."""
    if results_dict:
        for api_name, count in results_dict.items():
            if count > 0:
                st.success("**" + api_name + ":** Found " + str(count) + " matching articles")
            else:
                st.warning("**" + api_name + ":** No matching articles found")
    else:
        st.info("No source verification data available (API keys may be missing).")


def render_technical_metrics(breakdown):
    """Render the score breakdown table in Advanced Analysis."""
    if not breakdown:
        return
    bd_data = {"Signal": [], "Score": [], "Weight": []}
    label_map = {
        "source_reputation": "Source Reputation",
        "external_evidence": "External Evidence",
        "fact_check": "Fact Check",
        "timeline": "Timeline",
        "manipulation": "Manipulation",
        "headline": "Headline",
        "ml_prediction": "ML Prediction"
    }
    for key, data in breakdown.items():
        label = label_map.get(key, key.replace("_", " ").title())
        bd_data["Signal"].append(label)
        raw = data.get("raw", "N/A")
        if isinstance(raw, float):
            bd_data["Score"].append(f"{raw:.1f}")
        else:
            bd_data["Score"].append(str(raw))
        bd_data["Weight"].append(str(data.get("weight", "")) + "%")

    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Signal**")
        for s in bd_data["Signal"]:
            st.markdown(f"<div style='font-size:13px;color:#94a3b8;padding:2px 0;'>{s}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("**Raw Score**")
        for s in bd_data["Score"]:
            st.markdown(f"<div style='font-size:13px;color:#e2e8f0;padding:2px 0;'>{s}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("**Weight**")
        for w in bd_data["Weight"]:
            st.markdown(f"<div style='font-size:13px;color:#94a3b8;padding:2px 0;'>{w}</div>", unsafe_allow_html=True)


def render_sentiment_analysis(sentiment_result):
    """Render sentiment analysis inside Advanced Analysis."""
    polarity = sentiment_result.get("polarity", 0)
    polarity_label = "Positive" if polarity > 0.1 else ("Negative" if polarity < -0.1 else "Neutral")
    man_risk = sentiment_result.get("manipulation_risk", "Low")
    words = sentiment_result.get("sensational_words", [])
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("Polarity", "{:.2f}".format(polarity) + " (" + polarity_label + ")")
    with cols[1]:
        risk_color = "green" if man_risk == "Low" else ("yellow" if man_risk == "Medium" else "red")
        c_map = {"green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171"}
        color = c_map.get(risk_color, "#94a3b8")
        st.markdown(f"<div style='font-size:13px;color:#94a3b8;'>Manipulation Risk</div><div style='font-size:22px;font-weight:700;color:{color};'>{man_risk}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.metric("Sensational Words", len(words))
    if words:
        st.write("**Detected:** " + ", ".join(words))


def render_virality_analysis(virality_result):
    """Render virality analysis inside Advanced Analysis."""
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Mentions", virality_result.get("mentions", 0))
    with col2:
        spread_level = virality_result.get("level", "Low")
        spread_color = "green" if spread_level == "Low" else ("yellow" if spread_level == "Medium" else "red")
        c_map = {"green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171"}
        color = c_map.get(spread_color, "#94a3b8")
        st.markdown(f"<div style='font-size:13px;color:#94a3b8;'>Spread Level</div><div style='font-size:22px;font-weight:700;color:{color};'>{spread_level}</div>", unsafe_allow_html=True)


def render_timeline_analysis(timeline_result):
    """Render timeline analysis inside Advanced Analysis."""
    tl_status = timeline_result.get("status", "Unknown")
    tl_years = timeline_result.get("years_old")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Status", tl_status)
    with col2:
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


def render_risk_analysis(risk_result):
    """Render risk analysis inside Advanced Analysis."""
    risk_categories = risk_result.get("risk_categories", ["General"])
    st.write("**Categories:** " + ", ".join(risk_categories))
    if risk_result.get("high_risk", False):
        st.error("High Risk - involves sensitive topics (Health, Political, Financial, or Scam)")
    else:
        st.success("Low Risk - general content")


def render_source_comparison(source_comparison_result):
    """Render source consensus inside Advanced Analysis."""
    agmt = source_comparison_result.get("agreement", 0)
    classification = source_comparison_result.get("classification", "N/A")
    sources_checked = source_comparison_result.get("sources_checked", 0)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Agreement", str(agmt) + "%")
    with col2:
        cls_color = "green" if classification == "High Agreement" else ("yellow" if classification == "Moderate Agreement" else "red")
        c_map = {"green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171"}
        color = c_map.get(cls_color, "#94a3b8")
        st.markdown(f"<div style='font-size:13px;color:#94a3b8;'>Consensus</div><div style='font-size:22px;font-weight:700;color:{color};'>{classification}</div>", unsafe_allow_html=True)
    with col3:
        st.metric("Sources", sources_checked)


def render_headline_analysis(headline_result):
    """Render headline analysis inside Advanced Analysis."""
    hl_score = headline_result.get("score", 0)
    hl_risk = headline_result.get("risk", "Low")
    hl_reasons = headline_result.get("reasons", [])
    col1, col2 = st.columns(2)
    with col1:
        risk_color = "green" if hl_risk == "Low" else ("yellow" if hl_risk == "Medium" else "red")
        c_map = {"green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171"}
        color = c_map.get(risk_color, "#94a3b8")
        st.markdown(f"<div style='font-size:13px;color:#94a3b8;'>Headline Risk</div><div style='font-size:22px;font-weight:700;color:{color};'>{hl_risk}</div>", unsafe_allow_html=True)
    with col2:
        st.metric("Sensationalism Score", str(hl_score) + "/100")
    if hl_reasons:
        for reason in hl_reasons:
            st.write("• " + reason)


def render_rewrite_analysis(rewrite_result):
    """Render content manipulation detection inside Advanced Analysis."""
    rw_similarity = rewrite_result.get("similarity", 0)
    rw_risk = rewrite_result.get("risk", "High")
    rw_explanation = rewrite_result.get("explanation", "")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Source Similarity", str(rw_similarity) + "%")
    with col2:
        risk_color = "green" if rw_risk == "Low" else ("yellow" if rw_risk == "Medium" else "red")
        c_map = {"green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171"}
        color = c_map.get(risk_color, "#94a3b8")
        st.markdown(f"<div style='font-size:13px;color:#94a3b8;'>Manipulation Risk</div><div style='font-size:22px;font-weight:700;color:{color};'>{rw_risk}</div>", unsafe_allow_html=True)
    if rw_explanation:
        st.info(rw_explanation)


def render_similarity_analysis(similarity_score):
    """Render similarity analysis inside Advanced Analysis."""
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Similarity Score", str(similarity_score) + "%")
    with col2:
        if similarity_score > 80:
            st.success("Strong alignment between claim and article")
        elif similarity_score > 50:
            st.info("Moderate alignment")
        else:
            st.warning("Weak alignment - claim may not match article content")


def render_download_section():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a2236,#1e2a40);border:1px solid #2a3456;border-radius:14px;padding:20px 24px;margin:16px 0;">
        <div style="font-size:16px;font-weight:600;color:#f1f5f9;">📄 Download Report</div>
        <div style="font-size:13px;color:#94a3b8;">Download a detailed analysis report in TXT or PDF format.</div>
    </div>
    """, unsafe_allow_html=True)
