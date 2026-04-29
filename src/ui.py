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
        /* Background */
        .stApp {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #f8fafc;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Text area styling */
        textarea {
            border-radius: 12px !important;
            padding: 12px !important;
            font-size: 15px !important;
        }

        /* Button styling */
        .stButton>button {
            background-color: #22c55e;
            color: white;
            border-radius: 12px;
            height: 3em;
            width: 100%;
            font-size: 16px;
            border: none;
        }

        .stButton>button:hover {
            background-color: #16a34a;
            color: white;
        }

        /* Headers */
        h1, h2, h3 {
            color: #f1f5f9;
            text-align: center;
        }

        /* Info boxes spacing */
        .stAlert {
            border-radius: 10px;
        }

        /* Divider */
        hr {
            border: 1px solid #334155;
        }
        </style>
    """, unsafe_allow_html=True)


def show_header():
    st.markdown("""
        <h1> Fake News Detector AI</h1>
        <p style='text-align: center; color: #94a3b8; font-size: 16px;'>
        Analyze news using Machine Learning + Real-time Verification
        </p>
    """, unsafe_allow_html=True)


def show_footer():
    st.markdown("---")
    st.markdown("""
        <p style='text-align: center; color: #94a3b8; font-size: 13px;'>
         This AI-generated tool is for informational purposes only. 
        Please verify news from reliable sources before making conclusions.
        </p>
    """, unsafe_allow_html=True)
