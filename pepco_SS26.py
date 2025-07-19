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
def format_number(value, currency):
    """Format number based on currency requirements"""
    try:
        # Convert string to float if needed
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
            
        # Format currencies that use comma as decimal separator
        if currency in ['EUR', 'BGN', 'BAM', 'RON', 'PLN',]:
            formatted = f"{float(value):,.2f}".replace(".", ",")
            # Handle cases like "1,20" becoming "1,20" (correct) vs "1200,00" becoming "1.200,00"
            if ',' in formatted:
                parts = formatted.split(',')
                parts[0] = parts[0].replace('.', '')  # Remove thousand separators
                formatted = ','.join(parts)
            return formatted
        # Format currencies that use whole numbers
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value)  # Return as-is if formatting fails

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

# ========== PEPCO FUNCTIONS ==========

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

def format_product_translations(product_name, translation_row):
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
    
    # 3. Define the exact output order you want
    language_order = [
        'AL', 'BG', 'BIH', 'CZ', 'DE', 'EE', 'ES', 
        'GR', 'HR', 'HU', 'IT', 'LT', 'LV', 'MK',
        'PL', 'PT', 'RO', 'RS', 'SI', 'SK'
    ]
    
    # 4. Process languages in specified order
    for lang in language_order:
        if lang in combined_languages:
            formatted.append(f"|{lang}| {combined_languages[lang]}")
        elif pd.notna(translation_row.get(lang)):
            formatted.append(f"|{lang}| {translation_row[lang]}")
        else:
            formatted.append(f"|{lang}| {product_name}")
    
    return " ".join(formatted)

COLLECTION_MAPPING = {
    # Baby boys outerwear
    'b': {
        'CROCO CLUB': 'MODERN 1',
        'LITTLE SAILOR': 'MODERN 2',
        'EXPLORE THE WORLD': 'MODERN 3',
        'JURASIC ADVENTURE': 'MODERN 4',
        'WESTERN SPIRIT': 'CLASSIC 1',
        'SUMMER FUN': 'CLASSIC 2'
    },
    # Baby girls outerwear
    'a': {
        'Rainbow Girl': 'MODERN 1',
        'NEONS PICNIC': 'MODERN 2',
        'COUNTRY SIDE': 'ROMANTIC 2',
        'ESTER GARDENG': 'ROMANTIC 3'
    },
    # Baby boys essentials
    'd': {
        'LITTLE TREASURE': 'MODERN 1',
        'DINO FRIENDS': 'CLASSIC 1',
        'EXOTIC ANIMALS': 'CLASSIC 2'
    },
    # Baby girls essentials
    'd_girls': {
        'SWEEET PASTELS': 'MODERN 1',
        'PORCELAIN': 'ROMANTIC 2',
        'SUMMER VIBE': 'ROMANTIC 3'
    },
    # Younger girls outerwear (from previous requirement)
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
    """Determine the classification type based on item classification text"""
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

        # Get classification and collection
        item_class_value = item_class.group(1).strip() if item_class else "UNKNOWN"
        class_type = get_classification_type(item_class_value)
        collection_value = collection.group(1).split("-")[0].strip() if collection else "UNKNOWN"

        # Apply collection transformation
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
    "Style": style_code.group() if style_code else "UNKNOWN",  # Changed from STYLE_CODE
    "Colour": colour,  # Changed from COLOUR
    "Supplier_product_code": supplier_code.group(1).strip() if supplier_code else "UNKNOWN",
    "Item_classification": item_class_value,
    "Supplier_name": supplier_name.group(1).strip() if supplier_name else "UNKNOWN",
    "today_date": datetime.today().strftime('%d-%m-%Y'),
    "Collection": collection_value,  # Changed from COLLECTION
    "Colour_SKU": f"{colour} • SKU {sku}",  # Changed from COLOUR_SKU
    "Style_Merch_Season": f"STYLE {style_code.group()} • {style_suffix} • Batch No./ " if style_code else "STYLE UNKNOWN",  # Changed from STYLE
    "Batch": f"Data e prodhimit: {batch}",
    "barcode": barcode
} for sku, barcode in zip(skus, valid_barcodes)]

        return result

    except Exception as e:
        st.error(f"PDF error: {str(e)}")
        return None

def process_pepco_pdf(uploaded_pdf):
    translations_df = load_product_translations()
    
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

            df = pd.DataFrame(result_data)
            product_row = filtered[filtered['PRODUCT_NAME'] == product_type]
            if not product_row.empty:
                df['product_name'] = format_product_translations(product_type, product_row.iloc[0])
            else:
                df['product_name'] = ""

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
    "Colour_SKU", "Style_Merch_Season", "Batch", "barcode", "EUR", "BGN", "BAM", 
    "PLN", "RON", "CZK", "MKD", "RSD", "HUF", "product_name"
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

# ========== PEP&CO FUNCTIONS ==========

def extract_story(page1_text):
    match = re.search(r"Story\s+(.+)", page1_text)
    return match.group(1).split("-")[0].strip() if match else "UNKNOWN"

def extract_pack_details(text):
    details = {}
    order = re.search(r"Order Number\s+(\d+)", text)
    details["Order_Number"] = order.group(1).strip() if order else "UNKNOWN"

    supplier = re.search(r"Supplier name\s+([^\n]+)", text)
    details["Supplier_name"] = supplier.group(1).strip() if supplier else "UNKNOWN"

    handover = re.search(r"Handover Date\s+(\d{4}-\d{2}-\d{2})", text)
    details["Handover_Date"] = handover.group(1) if handover else None

    sku_match = re.search(r"\b(\d{6})\b", text)
    details["Pack_SKU"] = sku_match.group(1) if sku_match else "UNKNOWN"

    barcode_match = re.search(r"\b(\d{13})\b", text)
    details["Pack_Barcode"] = barcode_match.group(1) if barcode_match else "UNKNOWN"

    return details

def extract_table_from_page2(page2_text):
    try:
        lines = [line.strip() for line in page2_text.splitlines() if line.strip()]
        
        # Find the starting point of the table data
        data_start = None
        for i, line in enumerate(lines):
            if re.match(r"^\d{6}$", line):  # Looking for a 6-digit SKU
                data_start = i
                break
                
        if data_start is None:
            st.warning("⚠️ Could not find table start in page 2")
            return []
        
        entries = []
        while data_start + 6 < len(lines):  # Reduced from 10 to 6 for safety
            try:
                sku = lines[data_start]
                desc = lines[data_start + 1]
                barcode = lines[data_start + 2]
                style = lines[data_start + 6]
                
                # Validation checks
                if (re.match(r"^\d{6}$", sku) and 
                    re.match(r"^\d{13}$", barcode) and 
                    re.match(r"^\d{6}$", style)):
                    
                    clean_desc = desc.split(":")[0].strip() if ":" in desc else desc.strip()
                    entries.append({
                        "sku": sku,
                        "sku_description": clean_desc,
                        "barcode": barcode,
                        "style": style
                    })
                    data_start += 11  # Move to next entry
                else:
                    data_start += 1  # Move forward slowly if validation fails
                    
            except IndexError:
                break  # Reached end of lines
                
        if not entries:
            st.warning("⚠️ No valid entries found in the table")
            
        return entries
        
    except Exception as e:
        st.error(f"Error extracting table: {str(e)}")
        return []

def process_pep_and_co_pdf(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        if len(doc) < 2:
            st.error("❌ PDF must have at least 2 pages.")
            return None

        story_text = doc[0].get_text()
        page2_text = doc[1].get_text()

        story = extract_story(story_text)
        details = extract_pack_details(story_text)
        entries = extract_table_from_page2(page2_text)

        if not entries:
            st.error("❌ No product entries found in the PDF")
            return None

        # Initialize variables to store processed data
        processed_df = None

        with st.form("pepandco_form"):
            colour = st.text_input("Enter Colour:", key="pepandco_colour")
            sku_description_input = st.text_input("Enter Description:", key="pepandco_description")

            group_options = [
                "KIDSWEAR / BABY CLOTHING",
                "KIDSWEAR / KIDS CLOTHING",
                "MENSWEAR / MENS CLOTHING",
                "WOMENSWEAR / WOMENS CLOTHING",
                "KIDSWEAR / BABY ESSENTIALS",
                "KIDSWEAR / KIDS ESSENTIALS",
                "MENSWEAR / MENS ESSENTIALS",
                "WOMENSWEAR / WOMENS ESSENTIALS"
            ]
            selected_group = st.selectbox(
                "Select Department", 
                options=group_options,
                key="pepandco_department"
            )

            batch_options = ["Order Number", "Handover Date"]
            batch_choice = st.selectbox(
                "Select Batch Source", 
                options=batch_options,
                key="pepandco_batch_source"
            )

            if st.form_submit_button("Process Data"):
                if not colour or not sku_description_input:
                    st.error("❌ Please enter both colour and description")
                    return None

                processed_data = []
                for entry in entries:
                    if batch_choice == "Order Number":
                        batch_info = f"Batch no. {details['Order_Number']}"
                    else:
                        try:
                            handover_date = datetime.strptime(details["Handover_Date"], "%Y-%m-%d")
                            batch_date = handover_date - timedelta(days=20)
                            batch_info = f"Batch no. {batch_date.strftime('%m%Y')}"
                        except:
                            batch_info = "Batch no. UNKNOWN"

                    # Add the new sku_description_2 field with (Ratio Packs)
                    sku_description_2 = f"{sku_description_input} (Ratio Packs)"

                    processed_data.append({
                        "Order_Number": details.get("Order_Number", "UNKNOWN"),
                        "Supplier_name": details.get("Supplier_name", "UNKNOWN"),
                        "today_date": datetime.today().strftime('%d/%m/%Y'),
                        "Pack_SKU": details.get("Pack_SKU", "UNKNOWN"),
                        "Pack_Barcode": details.get("Pack_Barcode", "UNKNOWN"),
                        "Department": selected_group,
                        "story": story,
                        "sku_description": sku_description_input,
                        "sku_description_2": sku_description_2,  # New field added
                        "COLOUR_SKU": f"{colour} • SKU {entry['sku']}",
                        "STYLE": f"STYLE {entry['style']} • H/W26",
                        "STYLE_code": entry['style'],
                        "Batch": batch_info,
                        "barcode": entry['barcode'],
                        "colour": colour
                    })

                processed_df = pd.DataFrame(processed_data)[[
                    "Order_Number", "Supplier_name", "today_date",
                    "Pack_SKU", "Pack_Barcode", "Department",
                    "story", "sku_description", "sku_description_2",  # Include new field
                    "COLOUR_SKU", "STYLE", "STYLE_code", 
                    "Batch", "barcode", "colour"
                ]]

        # Display results and download button outside the form
        if processed_df is not None:
            st.success("✅ Processing complete!")
            st.subheader("Edit Before Download")
            edited_df = st.data_editor(processed_df)

            csv_buffer = StringIO()
            edited_df.to_csv(csv_buffer, sep=';', quoting=csv.QUOTE_ALL, index=False)
            
            st.download_button(
                "📥 Download CSV",
                csv_buffer.getvalue().encode('utf-8-sig'),
                file_name=f"pepco_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
                
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        return None


# ========== MAIN APP ==========
def main():
    st.title("PEPCO/PEP&CO Data Processor")

    # Initialize session state for brand selection
    if 'selected_brand' not in st.session_state:
        st.session_state.selected_brand = "PEPCO"

    # Create a container for the radio buttons
    with st.container():
        brand = st.radio(
            "Select Brand",
            ("PEPCO", "PEP&CO"),
            key="main_brand_selector",
            index=0 if st.session_state.selected_brand == "PEPCO" else 1
        )
        st.session_state.selected_brand = brand

    if brand == "PEPCO":
        pepco_section()
    else:
        pepandco_section()

def pepco_section():
    st.subheader("PEPCO Data Processing")
    uploaded_pdf = st.file_uploader(
        "Upload PEPCO Data file",
        type=["pdf"],
        key="pepco_unique_uploader"
    )
    if uploaded_pdf:
        process_pepco_pdf(uploaded_pdf)

def pepandco_section():
    st.subheader("PEP&CO Data Processing")
    uploaded_file = st.file_uploader(
        "Upload PEP&CO PDF",
        type="pdf",
        key="pepandco_unique_uploader"
    )
    if uploaded_file:
        process_pep_and_co_pdf(uploaded_file)

if __name__ == "__main__":
    main()

st.markdown("---")
st.caption("This app developed by Ovi")
