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

# ========== WASHING CODE MAPPING ==========
WASHING_CODES = {
    '1': '১২৩৪৫',
    '2': '১৪৭৮৫',
    '3': '৩৬৯৮৫',
    '4': '২৫৮৯৬',
    '5': '৩২১৪৫',
    '6': '৪৫৬৯৮',
    '7': '৭৮৯৪৫',
    '8': '৫৮৯৬৫',
    '9': '৫৮৭৪৫',
    '10': '০৩২১৪',
    '11': '০১৪৭৮',
    '12': '৯৬৩০২',
    '13': '৮৫২০১',
    '14': '৭৪১৯৬',
    '15': '২০১০৫'
}

# ========== PRICE DATA (For PEPCO) ==========
PRICE_DATA = {
    'PLN': [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.3, 1.5, 1.8, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 12, 14, 15, 17, 18, 20, 22, 25, 27, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 250],
    'EUR': [0.05, 0.05, 0.1, 0.1, 0.1, 0.15, 0.2, 0.2, 0.25, 0.25, 0.35, 0.4, 0.4, 0.45, 0.5, 0.65, 0.8, 0.9, 1, 1.2, 1.3, 1.5, 1.8, 2, 2.3, 2.5, 3, 3.5, 4, 4.5, 4.5, 5, 5.5, 6, 6.5, 7, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25, 28, 30, 33, 35, 38, 40, 43, 45, 48, 50, 53],
    'BGN': [0.10, 0.10, 0.20, 0.20, 0.20, 0.29, 0.39, 0.39, 0.49, 0.49, 0.68, 0.78, 0.78, 0.88, 0.98, 1.27, 1.56, 1.76, 1.96, 2.35, 2.54, 2.93, 3.52, 3.91, 4.50, 4.89, 5.87, 6.85, 7.82, 8.80, 8.80, 9.78, 10.76, 11.73, 12.71, 13.69, 17.60, 19.56, 21.51, 23.47, 27.38, 29.34, 31.29, 33.25, 37.16, 39.12, 43.03, 44.98, 46.94, 48.90, 54.76, 58.67, 64.54, 68.45, 74.32, 78.23, 84.10, 88.01, 93.88, 97.79, 103.66],
    'BAM': [0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.6, 0.6, 0.7, 0.8, 1, 1.25, 1.5, 1.75, 2, 2.3, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 9.5, 10, 11, 12, 13, 15, 17, 20, 22, 23, 25, 30, 33, 35, 38, 40, 43, 45, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 125],
    'RON': [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.3, 1.4, 1.5, 1.8, 2, 2.5, 3, 3.5, 4.5, 5, 6, 7, 8, 9, 9.5, 10, 13, 15, 16, 18, 19, 21, 25, 30, 32, 35, 40, 45, 50, 55, 60, 65, 70, 80, 85, 90, 95, 100, 105, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 220, 260],
    'CZK': [1, 2, 2, 2, 3, 4, 5, 5, 6, 6, 9, 9, 9, 12, 12, 15, 20, 22, 25, 27, 30, 35, 40, 50, 55, 60, 70, 80, 90, 100, 110, 120, 130, 150, 170, 180, 200, 250, 280, 300, 330, 350, 390, 420, 450, 480, 510, 540, 570, 600, 670, 740, 800, 880, 950, 1000, 1050, 1100, 1150, 1200, 1300],
    'RSD': [5, 5, 10, 15, 15, 20, 20, 25, 30, 30, 40, 45, 50, 50, 60, 70, 90, 100, 120, 130, 150, 180, 200, 250, 270, 300, 350, 400, 450, 550, 570, 600, 650, 700, 800, 900, 1000, 1200, 1300, 1500, 1600, 1700, 1800, 2000, 2200, 2500, 2500, 2600, 2800, 3000, 3300, 3600, 4000, 4500, 5000, 5300, 5600, 5900, 6200, 6500, 6700],
    'HUF': [12, 25, 35, 35, 45, 55, 60, 65, 75, 100, 120, 130, 150, 180, 200, 250, 300, 350, 400, 430, 500, 550, 650, 750, 850, 1000, 1200, 1400, 1500, 1600, 1700, 1800, 2000, 2500, 2700, 2900, 3200, 3600, 4000, 4500, 4800, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 25000],
    'MKD': [3, 3, 6, 6, 6, 9, 12, 12, 15, 15, 21, 24, 24, 27, 30, 39, 48, 54, 60, 72, 78, 90, 108, 120, 138, 150, 180, 210, 240, 270, 270, 300, 330, 360, 390, 420, 540, 600, 660, 720, 840, 900, 960, 1020, 1140, 1200, 1320, 1380, 1440, 1500, 1680, 1800, 1980, 2100, 2280, 2400, 2580, 2700, 2880, 3000, 3180],
}

# ========== HELPER FUNCTIONS ==========
@st.cache_data(ttl=600)
def load_product_translations():
    try:
        sheet_id = "1ue68TSJQQedKa7sVBB4syOc0OXJNaLS7p9vSnV52mKA"
        sheet_name = "SS26 Product_Name"
        encoded_sheet_name = requests.utils.quote(sheet_name)
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
        
        df = pd.read_csv(url)
        if df.empty:
            st.error("Loaded translations but the sheet appears empty")
        return df
    except Exception as e:
        st.error(f"❌ Failed to load translations. Please check: {str(e)}")
        st.info("Ensure the sheet is shared with 'Anyone with the link can view'")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_material_translations():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdAQmBHwDEWCgmLdEdJc0HsFYpPSyERPHLwmr2tnTYU1BDWdBD6I0ZYfEDzataX0wTNhfLfnm-Te6w/pub?gid=1096440227&single=true&output=csv"
        df = pd.read_csv(url)
        
        if df.empty:
            st.error("Material translations sheet is empty")
            return pd.DataFrame()
        
        # Convert from wide to long format
        material_translations = []
        for _, row in df.iterrows():
            for lang in ['AL', 'BG', 'MK', 'RS']:
                material_translations.append({
                    'material': row['Name'],
                    'language': lang,
                    'translation': row[lang]
                })
        
        return pd.DataFrame(material_translations)
        
    except Exception as e:
        st.error(f"Failed to load material translations: {str(e)}")
        return pd.DataFrame()

def format_number(value, currency):
    """Format number based on currency requirements"""
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
            
        if currency in ['EUR', 'BGN', 'BAM', 'RON', 'PLN']:
            formatted = f"{float(value):,.2f}".replace(".", ",")
            if ',' in formatted:
                parts = formatted.split(',')
                parts[0] = parts[0].replace('.', '')
                formatted = ','.join(parts)
            return formatted
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value)

def find_closest_price(pln_value):
    try:
        pln_value = float(pln_value)
        closest_pln = min(PRICE_DATA['PLN'], key=lambda x: abs(x - pln_value))
        idx = PRICE_DATA['PLN'].index(closest_pln)
        return {
            currency: format_number(values[idx], currency) 
            for currency, values in PRICE_DATA.items() 
            if currency != 'PLN'
        }
    except (ValueError, TypeError):
        return None

def format_product_translations(product_name, translation_row, selected_material=None, material_translations=None):
    formatted = []
    country_suffixes = {
        'BiH': " Sastav materijala na ušivenoj etiketi.",
        'RS': " Sastav materijala nalazi se na ušivenoj etiketi.",
    }
    
    # 1. Always put EN first
    en_text = str(translation_row['EN']) if pd.notna(translation_row.get('EN')) else product_name
    formatted.append(f"|EN| {en_text}")
    
    # 2. Define languages that need special handling
    combined_languages = {
        'ES': f"{translation_row['ES']} / {translation_row['ES_CA']}" 
              if pd.notna(translation_row.get('ES_CA')) 
              else translation_row['ES']
    }
    
    # 3. Define the exact output order
    language_order = [
        'AL', 'BG', 'BiH', 'CZ', 'DE', 'EE', 'ES', 
        'GR', 'HR', 'HU', 'IT', 'LT', 'LV', 'MK',
        'PL', 'PT', 'RO', 'RS', 'SI', 'SK'
    ]
    
    # 4. Process languages in order
    for lang in language_order:
        if lang in combined_languages:
            text = combined_languages[lang]
        elif pd.notna(translation_row.get(lang)):
            text = translation_row[lang]
        else:
            text = product_name
        
        # Add material name for specific languages
        if selected_material and material_translations and lang in ['AL', 'BG', 'MK', 'RS']:
            material_text = material_translations.get(lang, "")
            if material_text:
                text = f"{text}: {material_text}"
        
        # Add country suffixes if needed
        if lang in country_suffixes:
            text += country_suffixes[lang]
            
        formatted.append(f"|{lang}| {text}")
    
    return " ".join(formatted)

# ========== PEPCO DATA PROCESSING ==========
COLLECTION_MAPPING = {
    'b': {
        'CROCO CLUB': 'MODERN 1',
        'LITTLE SAILOR': 'MODERN 2',
        'EXPLORE THE WORLD': 'MODERN 3',
        'JURASIC ADVENTURE': 'MODERN 4',
        'WESTERN SPIRIT': 'CLASSIC 1',
        'SUMMER FUN': 'CLASSIC 2'
    },
    'a': {
        'Rainbow Girl': 'MODERN 1',
        'NEONS PICNIC': 'MODERN 2',
        'COUNTRY SIDE': 'ROMANTIC 2',
        'ESTER GARDENG': 'ROMANTIC 3'
    },
    'd': {
        'LITTLE TREASURE': 'MODERN 1',
        'DINO FRIENDS': 'CLASSIC 1',
        'EXOTIC ANIMALS': 'CLASSIC 2'
    },
    'd_girls': {
        'SWEEET PASTELS': 'MODERN 1',
        'PORCELAIN': 'ROMANTIC 2',
        'SUMMER VIBE': 'ROMANTIC 3'
    },
    'yg': {
        'CUTE_JUMP': 'COLLECTION_1 G',
        'SWEET_HEART': 'COLLECTION_2 G',
        'DAISY': 'COLLECTION_3 G',
        'SPECIAL OCC': 'COLLECTION_4 G',
        'LILALOV': 'COLLECTION_5 G',
        'COOL GIRL': 'COLLECTION_6 G',
        'DEL MAR': 'COLLECTION_7 G'
    }
}

def get_classification_type(item_class):
    if not item_class:
        return None
        
    item_class = item_class.lower()
    
    if 'younger girls outerwear' in item_class:
        return 'yg'
    elif 'baby boys outerwear' in item_class:
        return 'b'
    elif 'baby girls outerwear' in item_class:
        return 'a'
    elif 'baby boys essentials' in item_class:
        return 'd'
    elif 'baby girls essentials' in item_class:
        return 'd_girls'
    return None

def extract_colour_from_page2(text, page_number=1):
    try:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        skip_keywords = ["PURCHASE", "COLOUR", "TOTAL", "PANTONE", "SUPPLIER", 
                        "PRICE", "ORDERED", "SIZES", "TPG", "TPX", "USD", "NIP", 
                        "PEPCO", "Poland", "ul. Strzeszyńska 73A, 60-479 Poznań", 
                        "NIP 782-21-31-157"]
        
        filtered_lines = [
            line for line in lines
            if all(keyword.lower() not in line.lower() for keyword in skip_keywords)
            and not re.match(r"^[\d\s,./-]+$", line)
        ]
        
        colour = "UNKNOWN"
        if filtered_lines:
            colour = filtered_lines[0]
            colour = re.sub(r'[\d\.\)\(]+', '', colour).strip().upper()
            
            if "MANUAL" in colour:
                st.warning(f"⚠️ Page {page_number}: 'MANUAL' detected in colour field")
                manual_colour = st.text_input(
                    f"Enter Colour (Page {page_number}):", 
                    key=f"colour_manual_{page_number}"
                )
                return manual_colour.upper() if manual_colour else "UNKNOWN"
            
            return colour if colour else "UNKNOWN"
        
        st.warning(f"⚠️ Page {page_number}: Colour information not found in PDF")
        manual_colour = st.text_input(
            f"Enter Colour (Page {page_number}):", 
            key=f"colour_missing_{page_number}"
        )
        return manual_colour.upper() if manual_colour else "UNKNOWN"
        
    except Exception as e:
        st.error(f"Error extracting colour: {str(e)}")
        return "UNKNOWN"

def extract_data_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        if len(doc) < 3:
            st.error("PDF must have at least 3 pages.")
            return None

        page1 = doc[0].get_text()
        merch_code = re.search(r"Merch\s*code\s*\.{2,}\s*([\w/]+)", page1)
        season = re.search(r"Season\s*\.{2,}\s*(\w+)?\s*(\d{2})", page1)
        
        style_code = re.search(r"\b\d{6}\b", page1)
        style_suffix = ""
        
        if merch_code and season:
            merch_value = merch_code.group(1).strip()
            season_digits = season.group(2)
            style_suffix = f"{merch_value}{season_digits}"
        elif merch_code:
            style_suffix = merch_code.group(1).strip()

        collection = re.search(r"Collection\s*\.{2,}\s*(.+)", page1)
        date_match = re.search(r"Handover\s*date\s*\.{2,}\s*(\d{2}/\d{2}/\d{4})", page1)
        batch = "UNKNOWN"
        if date_match:
            try:
                batch = (datetime.strptime(date_match.group(1), "%d/%m/%Y") - timedelta(days=20)).strftime("%m%Y")
            except:
                pass

        order_id = re.search(r"Order\s*-\s*ID\s*\.{2,}\s*(.+)", page1)
        item_class = re.search(r"Item classification\s*\.{2,}\s*(.+)", page1)
        supplier_code = re.search(r"Supplier product code\s*\.{2,}\s*(.+)", page1)
        supplier_name = re.search(r"Supplier name\s*\.{2,}\s*(.+)", page1)

        item_class_value = item_class.group(1).strip() if item_class else "UNKNOWN"
        class_type = get_classification_type(item_class_value)
        collection_value = collection.group(1).split("-")[0].strip() if collection else "UNKNOWN"

        if class_type and class_type in COLLECTION_MAPPING:
            for orig_collection, new_collection in COLLECTION_MAPPING[class_type].items():
                if orig_collection.upper() in collection_value.upper():
                    collection_value = new_collection
                    break

        colour = extract_colour_from_page2(doc[1].get_text())
        page3 = doc[2].get_text()
        skus = re.findall(r"\b\d{8}\b", page3)
        all_barcodes = re.findall(r"\b\d{13}\b", page3)
        excluded = set(re.findall(r"barcode:\s*(\d{13});", page3))
        valid_barcodes = [b for b in all_barcodes if b not in excluded]

        result = [{
            "Order_ID": order_id.group(1).strip() if order_id else "UNKNOWN",
            "Style": style_code.group() if style_code else "UNKNOWN",
            "Colour": colour,
            "Supplier_product_code": supplier_code.group(1).strip() if supplier_code else "UNKNOWN",
            "Item_classification": item_class_value,
            "Supplier_name": supplier_name.group(1).strip() if supplier_name else "UNKNOWN",
            "today_date": datetime.today().strftime('%d-%m-%Y'),
            "Collection": collection_value,
            "Colour_SKU": f"{colour} • SKU {sku}",
            "Style_Merch_Season": f"STYLE {style_code.group()} • {style_suffix} • Batch No./ " if style_code else "STYLE UNKNOWN",
            "Batch": f"Data e prodhimit: {batch}",
            "barcode": barcode
        } for sku, barcode in zip(skus, valid_barcodes)]

        return result

    except Exception as e:
        st.error(f"PDF error: {str(e)}")
        return None

def process_pepco_pdf(uploaded_pdf):
    translations_df = load_product_translations()
    material_translations_df = load_material_translations()
    
    if uploaded_pdf and not translations_df.empty:
        result_data = extract_data_from_pdf(uploaded_pdf)
        
        if result_data:
            depts = translations_df['DEPARTMENT'].dropna().unique().tolist()
            selected_dept = st.selectbox(
                "Select Department",
                options=depts,
                key="pepco_dept_select"
            )

            filtered = translations_df[translations_df['DEPARTMENT'] == selected_dept]
            products = filtered['PRODUCT_NAME'].dropna().unique().tolist()
            product_type = st.selectbox(
                "Select Product Type",
                options=products,
                key="pepco_product_select"
            )
            
            # Material selection
            if not material_translations_df.empty:
                materials = material_translations_df['material'].dropna().unique().tolist()
                selected_materials = st.multiselect(
                    "Select Material(s)",
                    options=materials,
                    key="pepco_material_select"
                )
                
                # Prepare material translations dictionary
                material_trans_dict = {}
                for lang in ['AL', 'BG', 'MK', 'RS']:
                    trans_list = []
                    for material in selected_materials:
                        trans = material_translations_df[
                            (material_translations_df['material'] == material) & 
                            (material_translations_df['language'] == lang)
                        ]
                        if not trans.empty:
                            trans_list.append(trans['translation'].iloc[0])
                    if trans_list:
                        material_trans_dict[lang] = ", ".join(trans_list)
            else:
                selected_materials = None
                material_trans_dict = None

            # Washing code selection (simplified to show only code numbers)
            washing_code = st.selectbox(
                "Select Washing Code",
                options=list(WASHING_CODES.keys()),
                key="pepco_washing_code"
            )

            df = pd.DataFrame(result_data)
            product_row = filtered[filtered['PRODUCT_NAME'] == product_type]
            
            if not product_row.empty:
                df['product_name'] = format_product_translations(
                    product_type,
                    product_row.iloc[0],
                    selected_materials,
                    material_trans_dict
                )
            else:
                df['product_name'] = ""

            # Add washing code to the dataframe
            df['washing_code'] = WASHING_CODES[washing_code]

            pln_price = st.number_input(
                "Enter PLN Price",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key="pepco_pln_price"
            )
            
            if pln_price:
                currency_values = find_closest_price(pln_price)
                if currency_values:
                    for cur in ['EUR', 'BGN', 'BAM', 'RON', 'CZK', 'MKD', 'RSD', 'HUF']:
                        df[cur] = currency_values.get(cur, "")
                    df['PLN'] = format_number(pln_price, 'PLN')

                    final_cols = [
                        "Order_ID", "Style", "Colour", "Supplier_product_code", 
                        "Item_classification", "Supplier_name", "today_date", "Collection", 
                        "Colour_SKU", "Style_Merch_Season", "Batch", "barcode", "washing_code",
                        "EUR", "BGN", "BAM", "PLN", "RON", "CZK", "MKD", "RSD", "HUF", "product_name"
                    ]

                    st.success("✅ Done!")
                    st.subheader("Edit Before Download")

                    edited_df = st.data_editor(df)

                    csv_buffer = StringIO()
                    writer = pycsv.writer(csv_buffer, delimiter=';', quoting=pycsv.QUOTE_ALL)
                    writer.writerow(edited_df.columns)
                    for row in edited_df.itertuples(index=False):
                        writer.writerow(row)

                    st.download_button(
                        "📥 Download CSV",
                        csv_buffer.getvalue().encode('utf-8-sig'),
                        file_name=f"{os.path.splitext(uploaded_pdf.name)[0]}.csv",
                        mime="text/csv"
                    )

# ========== MAIN APP ==========
def main():
    st.title("PEPCO Data Processor")
    pepco_section()

def pepco_section():
    st.subheader("PEPCO Data Processing")
    uploaded_pdf = st.file_uploader(
        "Upload PEPCO Data file",
        type=["pdf"],
        key="pepco_unique_uploader"
    )
    if uploaded_pdf:
        process_pepco_pdf(uploaded_pdf)

if __name__ == "__main__":
    main()

st.markdown("---")
st.caption("This app developed by Ovi")
