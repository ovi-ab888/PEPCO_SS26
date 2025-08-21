
import os
import streamlit as st

def hide_github(also_hide_toolbar: bool = False):
    """
    Hide the GitHub button/link in Streamlit's top-right header.
    Set also_hide_toolbar=True to hide the entire toolbar (all icons).
    Call this immediately AFTER st.set_page_config(...).
    """
    css = """
    <style>
    /* --- Robust GitHub hide across header/toolbar/menus --- */
    header[data-testid="stHeader"] a[href*="github.com"] { display: none !important; }
    div[data-testid="stToolbar"] a[href*="github.com"]   { display: none !important; }
    div[data-testid="stToolbar"] a[title*="GitHub"]      { display: none !important; }
    div[data-testid="stToolbar"] button[title*="GitHub"] { display: none !important; }
    div[data-testid="stToolbar"] a[aria-label*="GitHub"] { display: none !important; }
    /* Kebab / overflow menu items that link to GitHub */
    ul[role="menu"] a[href*="github.com"]                { display: none !important; }
    /* Old Streamlit selectors for fallback */
    #MainMenu a[href*="github.com"]                      { display: none !important; }
    /* Optional nudge */
    div[data-testid="stToolbar"] { right: 0.5rem; }
    </style>
    """
    if also_hide_toolbar or os.environ.get("HIDE_ST_TOOLBAR") == "1":
        css = css.replace("</style>", "div[data-testid='stToolbar'] { display: none !important; } </style>")
    st.markdown(css, unsafe_allow_html=True)
