from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="ระบบสร้างทิคเก็ต GPS",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

html_file = Path(__file__).parent / "cs_ticket_generator.html"
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=780, scrolling=True)
