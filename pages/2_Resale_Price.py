import streamlit as st

st.set_page_config(page_title="Resale Price Prediction", page_icon="💰", layout="wide")

st.title("💰 Used Mobile Resale Price Prediction")
st.markdown("Enter the details of the used mobile phone below to get an estimated resale price.")

with st.form("resale_price_form"):
    st.subheader("Basic Information")
    col1, col2 = st.columns(2)
    with col1:
        brand = st.selectbox("Brand", ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi", "Vivo", "Oppo", "Realme", "Motorola", "Nothing", "Other"])
        release_year = st.number_input("Release Year", min_value=2010, max_value=2030, value=2022)
        chipset = st.text_input("Chipset", placeholder="e.g. A15 Bionic, Snapdragon 8 Gen 2")
    with col2:
        model = st.text_input("Model Name", placeholder="e.g. iPhone 13")
        os_type = st.selectbox("OS Type", ["Android", "iOS", "Other"])
        
    st.subheader("Hardware Specs")
    col3, col4 = st.columns(2)
    with col3:
        ram_gb = st.selectbox("RAM (GB)", [3, 4, 6, 8, 12, 16], index=3)
        battery_capacity = st.number_input("Battery Capacity (mAh)", min_value=1000, value=4500)
        processor_score = st.number_input("Processor Score", min_value=0, value=80000)
        has_5g = st.selectbox("5G Support", ["Yes", "No"])
    with col4:
        storage_gb = st.selectbox("Storage (GB)", [64, 128, 256, 512, 1024], index=1)
        screen_size_inches = st.number_input("Screen Size (inches)", min_value=3.0, value=6.5, step=0.1)
        camera_score = st.number_input("Camera Score", min_value=0, value=85)
        original_price = st.number_input("Original Price (₹)", min_value=0.0, value=50000.0)

    st.subheader("Purchase Details")
    col5, col6 = st.columns(2)
    with col5:
        purchase_year = st.number_input("Purchase Year", min_value=2010, max_value=2030, value=2023)
    with col6:
        age_months = st.number_input("Age (Months)", min_value=0, value=15)

    st.subheader("Condition Details")
    col7, col8 = st.columns(2)
    with col7:
        condition = st.selectbox("Overall Condition", ["Excellent", "Good", "Fair", "Poor"])
        screen_cracked = st.selectbox("Screen Cracked?", ["No", "Yes"])
        water_damage = st.selectbox("Water Damage?", ["No", "Yes"])
    with col8:
        battery_health = st.number_input("Battery Health (%)", min_value=0.0, max_value=100.0, value=85.5)
        body_damage = st.selectbox("Body Damage?", ["No", "Yes"])
        repair_history = st.selectbox("Repair History", ["None", "Repaired"])

    st.subheader("Accessories & Warranty")
    col9, col10 = st.columns(2)
    with col9:
        warranty_remaining_months = st.number_input("Warranty Remaining (Months)", min_value=0, value=6)
        charger_available = st.selectbox("Original Charger?", ["Yes", "No"])
    with col10:
        box_available = st.selectbox("Original Box?", ["Yes", "No"])

    submit_button = st.form_submit_button("Predict Resale Price")

if submit_button:
    if not model:
        st.error("Please fill in the Model Name.")
    else:
        with st.spinner("Predicting..."):
            from model_utils import load_resale_model, validate_device_specs, compute_engineered_features, estimate_resale_range, safe_encode, normalize_city_tier, SELLER_TYPE_MAP
            import pandas as pd
            import numpy as np
            from db_utils import insert_search_history
            
            val_error = validate_device_specs(brand, model, os_type, chipset)
            if val_error:
                st.error(f"Validation Error: {val_error}")
            else:
                bundle = load_resale_model()
                if bundle is None:
                    st.error("Model files not found. Cannot predict.")
                else:
                    rf_model = bundle['model']
                    encoders = bundle['encoders']
                    band_ranges = bundle['band_ranges']
                    band_names = bundle.get('band_names', {})
                    feature_columns = bundle['feature_columns']
                    engineered_features = bundle.get('engineered_features', [])
                    metrics = bundle.get('metrics', {})
                    TOTAL_BANDS = len(band_ranges)
                    
                    data = {
                        "brand": brand, "model": model, "release_year": release_year, "ram_gb": ram_gb,
                        "storage_gb": storage_gb, "screen_size_inches": screen_size_inches, 
                        "battery_capacity": battery_capacity, "processor_score": processor_score,
                        "camera_score": camera_score, "os_type": os_type, "chipset": chipset,
                        "has_5g": 1 if has_5g == "Yes" else 0, "original_price": original_price,
                        "purchase_year": purchase_year, "age_months": age_months, "usage_hours_per_day": 4.0,
                        "condition": condition, "battery_health": battery_health,
                        "screen_cracked": 1 if screen_cracked == "Yes" else 0,
                        "body_damage": 1 if body_damage == "Yes" else 0,
                        "repair_history": 1 if repair_history == "Repaired" else 0,
                        "water_damage": 1 if water_damage == "Yes" else 0,
                        "city_tier": 1, "seller_type": "Individual",
                        "warranty_remaining_months": warranty_remaining_months,
                        "box_available": 1 if box_available == "Yes" else 0,
                        "charger_available": 1 if charger_available == "Yes" else 0,
                        "market_demand_score": 7.0
                    }
                    
                    warnings = []
                    row = data.copy()
                    
                    # Compute engineered features first (as they don't require encoding)
                    row = compute_engineered_features(row)
                    
                    # Normalize specific fields
                    if 'city_tier' in row:
                        row['city_tier'] = normalize_city_tier(row['city_tier'])
                    if 'seller_type' in row:
                        row['seller_type'] = SELLER_TYPE_MAP.get(row['seller_type'], row['seller_type'])
                        
                    # Encode categorical fields
                    for col, le in encoders.items():
                        if col in row:
                            encoded_val, warning = safe_encode(le, row[col], col)
                            row[col] = encoded_val
                            if warning:
                                warnings.append(warning)
                                
                    try:
                        input_df = pd.DataFrame([row])[feature_columns]
                        predicted_band = rf_model.predict(input_df)[0]
                        proba = rf_model.predict_proba(input_df)[0]
                        confidence = float(np.max(proba))
                        
                        top_3_indices = np.argsort(proba)[::-1][:3]
                        top_3 = []
                        for idx in top_3_indices:
                            band_label = rf_model.classes_[idx]
                            if band_label in band_ranges:
                                r_low, r_high = estimate_resale_range(band_label, band_ranges, data, TOTAL_BANDS)
                                top_3.append({
                                    'band': int(band_label),
                                    'name': f"Rs.{r_low:,} - Rs.{r_high:,}",
                                    'probability': round(float(proba[idx]) * 100, 1)
                                })
                                
                        est_low, est_high = estimate_resale_range(predicted_band, band_ranges, data, TOTAL_BANDS)
                        display_range = f"Rs.{est_low:,} - Rs.{est_high:,}"
                        
                        st.success("### Prediction Result")
                        st.markdown(f"# {display_range}")
                        conf_pct = round(confidence * 100, 1)
                        if conf_pct > 40:
                            st.info(f"**Confidence:** {conf_pct}%")
                        else:
                            st.warning(f"**Confidence:** {conf_pct}%")
                            
                        st.write("#### Top Predictions")
                        for pred in top_3:
                            st.progress(pred["probability"] / 100, text=f"{pred['name']} - {pred['probability']}%")
                            
                        if warnings:
                            for w in warnings:
                                st.warning(w)
                                
                        insert_search_history("Resale Price", brand, model, display_range)
                    except Exception as e:
                        st.error(f"Error predicting: {e}")
