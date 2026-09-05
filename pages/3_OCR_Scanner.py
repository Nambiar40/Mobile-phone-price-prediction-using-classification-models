import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from pyzbar.pyzbar import decode
from db_utils import insert_search_history
import os

st.set_page_config(page_title="OCR Price Prediction", page_icon="📸", layout="wide")

st.title("📸 OCR Price Prediction")
st.markdown("Upload a mobile phone invoice or image to extract details using OCR and predict the price range.")

# Set tesseract path for local Windows execution (if installed there). 
# On Streamlit Cloud, the default path works automatically after apt-get install tesseract-ocr.
if os.name == 'nt':
    tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    elif os.path.exists(r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

uploaded_file = st.file_uploader("Upload Image (Invoice, Box, etc.)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    if st.button("Extract Data & Predict"):
        with st.spinner("Processing image and running OCR..."):
            try:
                file_bytes = np.frombuffer(uploaded_file.getvalue(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if img is None:
                    st.error("Could not decode image.")
                else:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(gray)
                    
                    barcodes = decode(img)
                    barcode_data_list = []
                    for barcode in barcodes:
                        barcode_data = barcode.data.decode('utf-8')
                        barcode_type = barcode.type
                        barcode_data_list.append(f"[{barcode_type}] {barcode_data}")
                        text += f"\nBARCODE_CONTENT: {barcode_data}"
                        
                    extracted_data = {
                        'brand': '',
                        'model': '',
                        'original_price': '',
                        'purchase_year': '',
                        'barcode': ', '.join(barcode_data_list) if barcode_data_list else ''
                    }
                    
                    known_brands = ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Vivo', 'Oppo', 'Realme', 'Motorola', 'Nothing']
                    text_lower = text.lower()
                    for brand in known_brands:
                        if brand.lower() in text_lower:
                            extracted_data['brand'] = brand
                            break
                            
                    model_match = re.search(r'model[\s:]+([A-Za-z0-9\s-]+)', text, re.IGNORECASE)
                    if model_match:
                        model_str = model_match.group(1).split('\n')[0].strip()
                        model_str = re.sub(r'[,|\|]', '', model_str).strip()
                        extracted_data['model'] = model_str
                        
                    price_match = re.search(r'(?:rs\.?|₹|price)[\s:]*([\d,]+(?:\.\d{2})?)', text, re.IGNORECASE)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '')
                        try:
                            extracted_data['original_price'] = float(price_str)
                        except ValueError:
                            pass
                            
                    year_match = re.search(r'(?:year|mfg|date|purchase|bill)[\s:-]*(20[1-2][0-9])', text, re.IGNORECASE)
                    if not year_match:
                        lines = text.split('\n')
                        valid_lines = [l for l in lines if not re.search(r'(?i)shot on', l) and not re.search(r'20\d\d[\./-]\d\d[\./-]\d\d', l) and '|' not in l]
                        for line in valid_lines:
                            ym = re.search(r'\b(20[1-2][0-9])\b', line)
                            if ym:
                                year_match = ym
                                break
                                
                    if year_match:
                        extracted_data['purchase_year'] = int(year_match.group(1))
                        
                    price_val = extracted_data.get('original_price', '')
                    price_display = f"Rs.{price_val}" if price_val else "N/A"
                    insert_search_history("OCR Scan", extracted_data.get('brand') or 'Unknown', extracted_data.get('model') or 'Unknown', price_display)
                    
                    st.success("Successfully extracted data from the image!")
                    
                    st.subheader("Extracted Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Brand", extracted_data.get("brand") or "N/A")
                        st.metric("Original Price", extracted_data.get("original_price") or "N/A")
                    with col2:
                        st.metric("Model", extracted_data.get("model") or "N/A")
                        st.metric("Purchase Year", extracted_data.get("purchase_year") or "N/A")
                        
                    if extracted_data.get("barcode"):
                        st.info(f"**Barcode Detected:** {extracted_data.get('barcode')}")
                        
                    with st.expander("View Raw Extracted Text"):
                        st.text(text)
                        
                    st.info("You can use these details in the Resale Price Prediction page to get an accurate estimate.")
                    
            except Exception as e:
                st.error(f"Error processing image: {e}")
