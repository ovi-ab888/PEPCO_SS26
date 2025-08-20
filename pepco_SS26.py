# -*- coding: utf-8 -*-
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import csv
from io import StringIO
import csv as pycsv
from datetime import datetime, timedelta
import os
import requests.utils

# ========== CONSTANTS AND MAPPINGS ==========
WASHING_CODES = {
    '1': '১২৩৪৫',
    '2': '১৪৭৮৫',
    '3': '১২৭৮৫',
    '4': '১৩৭৮৫',
    '5': '১২৩৮৫',
    '6': '১২৩৭৫',
    '7': '১২৩৪৮',
    '8': '১২৩৪৭',
    '9': '১২৩৪৫',
    '10': '১২৩৪৬',
    '11': '১২৩৪৭',
    '12': '১২৩৪৮',
    '13': '১২৩৪৯',
    '14': '১২৩৫০',
}

COLLECTION_MAPPING = {
    'yb': {
        'PEP YB OUTERWEAR G': 'PEP YB OUTERWEAR G',
        'PEP YB SWEAT FLEECE B': 'PEP YB SWEAT FLEECE B',
        'PEP YB T-SHIRT B': 'PEP YB T-SHIRT B',
        'PEP YB TROUSER B': 'PEP YB TROUSER B',
        'PEP YB NIGHTWEAR B': 'PEP YB NIGHTWEAR B',
        'PEP YB OUTERWEAR B': 'PEP YB OUTERWEAR B',
    },
    'yg': {
        'PEP YG OUTERWEAR G': 'PEP YG OUTERWEAR G',
        'PEP YG SWEAT FLEECE G': 'PEP YG SWEAT FLEECE G',
        'PEP YG T-SHIRT G': 'PEP YG T-SHIRT G',
        'PEP YG TROUSER G': 'PEP YG TROUSER G',
        'PEP YG NIGHTWEAR G': 'PEP YG NIGHTWEAR G',
    },
    'ob': {
        'PEP OB OUTERWEAR B': 'PEP OB OUTERWEAR B',
        'PEP OB SWEAT FLEECE B': 'PEP OB SWEAT FLEECE B',
        'PEP OB T-SHIRT B': 'PEP OB T-SHIRT B',
        'PEP OB TROUSER B': 'PEP OB TROUSER B',
        'PEP OB NIGHTWEAR B': 'PEP OB NIGHTWEAR B',
    },
    'og': {
        'PEP OG OUTERWEAR G': 'PEP OG OUTERWEAR G',
        'PEP OG SWEAT FLEECE G': 'PEP OG SWEAT FLEECE G',
        'PEP OG T-SHIRT G': 'PEP OG T-SHIRT G',
        'PEP OG TROUSER G': 'PEP OG TROUSER G',
        'PEP OG NIGHTWEAR G': 'PEP OG NIGHTWEAR G',
    },
    'baby_b': {
        'PEP BABY BOY': 'PEP BABY BOY',
    },
    'baby_g': {
        'PEP BABY GIRL': 'PEP BABY GIRL',
    }
}

# ========== HELPER FUNCTIONS ==========
@st.cache_data(ttl=600)
def load_price_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1v...EDzataX0wTNhfLfnm-Te6w/pub?gid=583402611&single=true&output=csv"
        df = pd.read_csv(url)
        
        if df.empty:
            st.error("Price data sheet is empty")
            return None
            
        price_data = {}
        for currency in df.columns:
            col = (
                df[currency]
                .astype(str)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )
            price_data[currency] = col.dropna().tolist()
        return price_data
    except Exception as e:
        st.error(f"Failed to load price data: {e}")
        return None


def format_number(value, currency):
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        eu_style = ['EUR', 'BGN', 'BAM', 'RON', 'PLN', 'CZK', 'MKD', 'RSD', 'HUF']
        if currency in eu_style:
            s = f"{float(value):.2f}"
            parts = s.split(".")
            return f"{parts[0]},{parts[1]}"
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return str(value)


def find_closest_price(pln_value):
    try:
        price_data = load_price_data()
        if not price_data or 'PLN' not in price_data:
            st.error("❌ Price data not available")
            return None

        target = float(str(pln_value).replace(',', '.'))
        pln_list = price_data['PLN']
        idx = min(range(len(pln_list)), key=lambda i: abs(pln_list[i] - target))

        if abs(pln_list[idx] - target) > 0.01:
            st.info(f"ℹ️ Nearest PLN in sheet: {pln_list[idx]:.2f} (you entered {target:.2f})")

        return {
            cur: format_number(price_data[cur][idx], cur)
            for cur in price_data.keys()
        }
    except Exception as e:
        st.error(f"Invalid price value: {e}")
        return None


def modify_collection(collection, item_class):
    if not item_class:
        return collection
    base = re.sub(r"\s+[BG]$", "", str(collection).strip(), flags=re.I)
    ic = item_class.lower()
    if any(x in ic for x in ['younger boys outerwear', 'older boys outerwear']):
        return f"{base} B"
    elif any(x in ic for x in ['older girls outerwear', 'younger girls outerwear']):
        return f"{base} G"
    return base

# ================== PDF PARSING HELPERS (abbrev for brevity) ==================
# ... (the rest of your existing parsing and UI code remains unchanged) ...

# ================== MAIN APP ==================
def app():
    st.title("PEPCO Order Support — SS26")

    uploaded_pdf = st.file_uploader("Upload Order PDF", type=["pdf"]) 

    if uploaded_pdf:
        # ... your earlier extraction/translations logic ...
        # Assume df and final_cols computed, plus selected_dept exists
        proceed = st.button("Proceed to Review and Download")
        if proceed:
            st.subheader("Preview & Edit Before Download")
            edited_df = st.data_editor(df[final_cols])

            # ======== DOWNLOAD BUTTON (FIXED FOR EXCEL) ========
            # Build CSV in Excel-friendly way
            csv_str = edited_df.to_csv(
                index=False,
                sep=",",
                quoting=pycsv.QUOTE_MINIMAL,
                lineterminator="\r\n"
            )
            csv_bytes = csv_str.encode("utf-8-sig")  # add BOM for Excel UTF-8

            base_name = os.path.splitext(uploaded_pdf.name)[0]
            dept = (edited_df["Dept"].iloc[0] if "Dept" in edited_df.columns else selected_dept).replace(" ", "_")
            style_val = str(edited_df["Style"].iloc[0]) if "Style" in edited_df.columns else "NA"
            download_name = f"{base_name}_{dept}_{style_val}.csv"

            st.download_button(
                label="📥 Download CSV",
                data=csv_bytes,
                file_name=download_name,
                mime="text/csv"
            )
        else:
            st.warning("Processing stopped - valid PLN price not found")


def pepco_section():
    st.write("")

if __name__ == "__main__":
    app()
