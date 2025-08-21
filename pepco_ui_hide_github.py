# ---- page config: must be the first Streamlit call ----
st.set_page_config(page_title="PEPCO Data Processor", page_icon="🧾", layout="wide")

# ---- hide GitHub icon (inline CSS) ----
st.markdown("""
<style>
/* header/toolbar/menu—সবখান থেকে GitHub লিংক hide */
header[data-testid="stHeader"] a[href*="github.com"] { display: none !important; }
div[data-testid="stToolbar"] a[href*="github.com"]   { display: none !important; }
div[data-testid="stToolbar"] a[title*="GitHub"]      { display: none !important; }
div[data-testid="stToolbar"] button[title*="GitHub"] { display: none !important; }
div[data-testid="stToolbar"] a[aria-label*="GitHub"] { display: none !important; }
ul[role="menu"] a[href*="github.com"]                { display: none !important; }  /* overflow menu */
#MainMenu a[href*="github.com"]                      { display: none !important; }  /* old selector */
div[data-testid="stToolbar"] { right: 0.5rem; }                                       /* optional nudge */
</style>
""", unsafe_allow_html=True)
