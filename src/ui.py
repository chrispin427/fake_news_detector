# src/ui.py
import streamlit as st


def apply_styles():
    st.set_page_config(page_title="AI Fact Checker", page_icon="\U0001f50d", layout="centered")
    st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#070b15 0%,#0f1529 40%,#141b2d 100%);color:#e2e8f0;}
h1,h2,h3,h4,h5,h6{color:#f1f5f9!important;font-weight:600!important;}
p,li,.stMarkdown,.stText{color:#cbd5e1!important;}
.stTextArea textarea{background:#1a2236!important;border:1px solid #2a3456!important;border-radius:14px!important;padding:16px!important;color:#e2e8f0!important;}
.stButton>button{background:linear-gradient(135deg,#22c55e,#16a34a)!important;color:white!important;border-radius:12px!important;height:3.2em!important;font-weight:600!important;box-shadow:0 4px 14px rgba(34,197,94,0.25)!important;}
.stMetric{background:#1a2236;border:1px solid #2a3456;border-radius:12px;padding:16px;}
.stMetric label{color:#94a3b8!important;font-size:13px!important;font-weight:500!important;text-transform:uppercase;}
.stMetric [data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:28px!important;font-weight:700!important;}
.stProgress>div>div{background-color:#22c55e!important;border-radius:8px;}
.stProgress>div{background-color:#2a3456!important;border-radius:8px;height:8px!important;}
.streamlit-expanderHeader{background:#1a2236!important;border:1px solid #2a3456!important;border-radius:10px!important;color:#e2e8f0!important;}
.stAlert{border-radius:10px!important;}
hr{border:none!important;height:1px!important;background:linear-gradient(90deg,transparent,#2a3456,transparent)!important;}
.section-header{display:flex;align-items:center;gap:10px;margin:24px 0 12px;}
.section-header .section-icon{font-size:20px;width:36px;height:36px;display:flex;align-items:center;justify-content:center;background:rgba(59,130,246,0.1);border-radius:10px;}
.section-header .section-title{font-size:18px!important;font-weight:600!important;color:#f1f5f9!important;margin:0!important;}
.status-badge{display:inline-block;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:600;text-transform:uppercase;}
.status-badge.green{background:rgba(34,197,94,0.15);color:#4ade80;}
.status-badge.yellow{background:rgba(245,158,11,0.15);color:#fbbf24;}
.status-badge.red{background:rgba(239,68,68,0.15);color:#f87171;}
.status-badge.blue{background:rgba(59,130,246,0.15);color:#60a5fa;}
[data-testid="stSidebar"]{background:#0f1529!important;border-right:1px solid #1e293b!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] li{color:#94a3b8!important;font-size:13px!important;}
.block-container{padding-top:24px!important;}
</style>""", unsafe_allow_html=True)

def render_hero():
    st.markdown('<div style="text-align:center;padding:32px 20px 16px;"><div style="display:inline-block;background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);border-radius:20px;padding:4px 14px;font-size:12px;color:#4ade80;font-weight:500;text-transform:uppercase;margin-bottom:16px;">AI-Powered Analysis</div><h1 style="font-size:2.6rem;font-weight:800;background:linear-gradient(135deg,#f1f5f9,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;">AI Fact Checker</h1><p style="font-size:16px;color:#94a3b8;max-width:600px;margin:0 auto;line-height:1.6;">Verify articles, social media posts, and news claims using machine learning, source verification, and evidence analysis.</p></div>', unsafe_allow_html=True)

def render_section_header(icon, title):
    st.markdown(f'<div class="section-header"><div class="section-icon">{icon}</div><div class="section-title">{title}</div></div>', unsafe_allow_html=True)

def render_verdict_card(verdict, score, explanation):
    if verdict in ("Highly Credible", "Likely Credible"):
        border, color, shadow = "#22c55e", "#4ade80", "rgba(34,197,94,0.1)"
    elif verdict == "Uncertain":
        border, color, shadow = "#f59e0b", "#fbbf24", "rgba(245,158,11,0.07)"
    else:
        border, color, shadow = "#ef4444", "#f87171", "rgba(239,68,68,0.1)"
    st.markdown(f'<div style="background:linear-gradient(135deg,#1a2236,#1e2a40);border:2px solid {border};border-radius:16px;padding:28px 32px;text-align:center;margin:16px 0;box-shadow:0 0 30px {shadow};"><div style="font-size:28px;font-weight:800;color:{color};">{verdict}</div><div style="font-size:48px;font-weight:800;color:{color};">{score}/100</div><div style="font-size:14px;color:#94a3b8;margin-top:8px;">{explanation}</div></div>', unsafe_allow_html=True)

def render_status_badge(label, level):
    colors = {"green":("rgba(34,197,94,0.15)","#4ade80"),"yellow":("rgba(245,158,11,0.15)","#fbbf24"),"red":("rgba(239,68,68,0.15)","#f87171"),"blue":("rgba(59,130,246,0.15)","#60a5fa")}
    bg, text = colors.get(level, colors["blue"])
    st.markdown(f'<span style="display:inline-block;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:600;text-transform:uppercase;background:{bg};color:{text};">{label}</span>', unsafe_allow_html=True)

def render_evidence_card(title, source, url=""):
    url_html = f'<div style="font-size:12px;color:#3b82f6;word-break:break-all;">\U0001f517 {url}</div>' if url else ""
    st.markdown(f'<div style="background:#1a2236;border:1px solid #2a3456;border-radius:10px;padding:14px 16px;margin:8px 0;"><div style="font-size:14px;font-weight:600;color:#e2e8f0;">{title}</div><div style="font-size:12px;color:#22c55e;font-weight:500;">\U0001f4f0 {source}</div>{url_html}</div>', unsafe_allow_html=True)

def render_download_section():
    st.markdown('<div style="background:linear-gradient(135deg,#1a2236,#1e2a40);border:1px solid #2a3456;border-radius:14px;padding:20px 24px;margin:16px 0;"><div style="font-size:16px;font-weight:600;color:#f1f5f9;">\U0001f4c4 Download Report</div><div style="font-size:13px;color:#94a3b8;">Download a detailed analysis report in TXT or PDF format.</div></div>', unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown('<div style="padding:8px 0;"><h1 style="font-size:22px;font-weight:800;background:linear-gradient(135deg,#f1f5f9,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px;">\U0001f50d AI Fact Checker</h1><p style="font-size:12px;color:#64748b;">v1.0</p></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### \U0001f4d6 About This Project")
        st.markdown("AI Fact Checker uses ML and multi-source verification to detect misinformation and assess credibility.")
        st.markdown("### \u2699\ufe0f How Analysis Works")
        st.markdown("**1. ML** - Analyzes text patterns to classify news.\n**2. Fact Check** - Cross-references claims.\n**3. Evidence** - Collects supporting articles.\n**4. Source Verification** - Evaluates domain reputation.\n**5. Multi-dimensional** - Sentiment, virality, risk, and timeline.")
        st.markdown("### \U0001f680 Future Features")
        st.markdown("- Browser extension\n- API access\n- Multi-language\n- Historical dashboard\n- Custom training")
        st.markdown("---")
        st.markdown('<p style="text-align:center;color:#64748b;font-size:12px;">AI Fact Checker v1.0</p>', unsafe_allow_html=True)

def show_footer():
    st.markdown("---")
    st.markdown('<div style="text-align:center;padding:8px 0;"><p style="color:#64748b;font-size:12px;margin:0;">\U0001f50d AI Fact Checker &bull; For informational purposes only.</p></div>', unsafe_allow_html=True)
