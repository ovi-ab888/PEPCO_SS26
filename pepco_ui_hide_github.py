import streamlit as st

# Inject CSS to hide only the GitHub icon in the top-right toolbar
st.markdown("""
<style>
div[data-testid="stToolbar"] a[href*="github.com"] {
    display: none !important;
}
div[data-testid="stToolbar"] { right: 0.5rem; }
</style>
""", unsafe_allow_html=True)
