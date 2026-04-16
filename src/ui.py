# src/ui.py
import streamlit as st

def apply_styles():
    st.set_page_config(
        page_title="Fake News Detector",
        page_icon="📰",
        layout="centered"
    )

    st.markdown("""
        <style>
        .main {
            background-color: #0E1117;
            color: white;
        }
        textarea {
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)


def show_header():
    st.title("📰 Fake News Detector AI")
    st.caption("AI-powered fake news detection system")


def show_footer():
    st.markdown("---")
    st.caption(
        "⚠️ THIS IS AI GENERATED. PLEASE USE FOR REFERENCE ONLY AND CONDUCT MORE RESEARCH REGARDING YOUR NEWS."
    )