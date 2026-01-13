"""
UI module for MateMaTeX.
Contains styles, sidebar, configuration, and results components.
"""

from pathlib import Path


def load_css() -> str:
    """Load the main CSS styles from file."""
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


def inject_styles():
    """Inject CSS styles into the Streamlit app."""
    import streamlit as st
    css = load_css()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
