import streamlit as st

st.set_page_config(page_title="Current Price Prediction", page_icon="📊", layout="wide")

st.title("📊 Current Market Price Prediction")
st.markdown("Enter the mobile phone details below to get an estimated market price.")

with st.form("current_price_form"):
    st.subheader("Basic Information")
    col1, col2 = st.columns(2)
    with col1:
        brand = st.selectbox("Brand", ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi", "Vivo", "Oppo", "Realme", "Motorola", "Nothing", "Other"])
        launch_year = st.number_input("Launch Year", min_value=2010, max_value=2030, value=2022)
    with col2:
        model_name = st.text_input("Model Name", placeholder="e.g. iPhone 13")
        os_type = st.selectbox("Operating System", ["Android", "iOS", "Other"])

    st.subheader("Display & Battery")
    col3, col4 = st.columns(2)
    with col3:
        display_size_inch = st.number_input("Display Size (inches)", min_value=3.0, max_value=10.0, value=6.1, step=0.1)
        refresh_rate_hz = st.number_input("Refresh Rate (Hz)", min_value=60, max_value=240, value=120)
        battery_mah = st.number_input("Battery Capacity (mAh)", min_value=1000, max_value=10000, value=5000)
    with col4:
        display_type = st.selectbox("Display Type", ["AMOLED", "OLED", "LCD", "IPS LCD", "TFT", "Other"])
        screen_to_body_ratio = st.number_input("Screen-to-body Ratio (%)", min_value=50.0, max_value=100.0, value=88.5, step=0.1)
        fast_charging_w = st.number_input("Fast Charging (W)", min_value=0, max_value=240, value=33)

    st.subheader("Memory & Performance")
    col5, col6 = st.columns(2)
    with col5:
        ram_gb = st.selectbox("RAM (GB)", [3, 4, 6, 8, 12, 16], index=3)
        expandable_storage = st.selectbox("Expandable Storage", ["Yes", "No"], index=1)
        cpu_score = st.number_input("CPU Score", min_value=0, value=85000)
    with col6:
        storage_gb = st.selectbox("Storage (GB)", [64, 128, 256, 512, 1024], index=1)
        chipset = st.text_input("Chipset", placeholder="e.g. Snapdragon 8 Gen 2")
        gpu_score = st.number_input("GPU Score", min_value=0, value=70000)

    st.subheader("Cameras")
    col7, col8 = st.columns(2)
    with col7:
        rear_camera_mp = st.number_input("Rear Camera (MP)", min_value=0, value=64)
    with col8:
        front_camera_mp = st.number_input("Front Camera (MP)", min_value=0, value=16)
    camera_setup = st.selectbox("Camera Setup", ["Single", "Dual", "Triple", "Quad"], index=2)

    st.subheader("Build & Additional Features")
    col9, col10 = st.columns(2)
    with col9:
        weight_g = st.number_input("Weight (g)", min_value=0, value=180)
        build_material = st.selectbox("Build Material", ["Glass", "Plastic", "Metal"])
        support_5g = st.selectbox("5G Support", ["Yes", "No"])
        water_resistance = st.selectbox("Water Resistance", ["Yes", "No"])
        fingerprint_sensor = st.selectbox("Fingerprint Sensor", ["Yes", "No"])
        bluetooth_version = st.number_input("Bluetooth Version", min_value=1.0, value=5.2, step=0.1)
        warranty_years = st.number_input("Warranty (Years)", min_value=0, value=1)
    with col10:
        thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, value=7.5, step=0.1)
        colors_available = st.number_input("Colors Available (Count)", min_value=1, value=3)
        dual_sim = st.selectbox("Dual SIM", ["Yes", "No"])
        wireless_charging = st.selectbox("Wireless Charging", ["Yes", "No"], index=1)
        face_unlock = st.selectbox("Face Unlock", ["Yes", "No"])
        wifi_version = st.number_input("Wi-Fi Version", min_value=4, value=6)

    submit_button = st.form_submit_button("Predict Current Price")

if submit_button:
    if not model_name or not chipset:
        st.error("Please fill in all required fields (Model Name, Chipset).")
    else:
        with st.spinner("Predicting..."):
            from model_utils import load_current_price_model, validate_device_specs
            import pandas as pd
            from db_utils import insert_search_history
            
            val_error = validate_device_specs(brand, model_name, os_type, chipset)
            if val_error:
                st.error(f"Validation Error: {val_error}")
            else:
                model, le = load_current_price_model()
                if model is None or le is None:
                    st.error("Model files not found. Cannot predict.")
                else:
                    expected_features = [
                        'brand', 'model_name', 'os', 'launch_year', '5g_support', 'dual_sim',
                        'expandable_storage', 'water_resistance', 'wireless_charging',
                        'fingerprint_sensor', 'face_unlock', 'gpu_score', 'cpu_score',
                        'screen_to_body_ratio', 'build_material', 'colors_available',
                        'warranty_years', 'bluetooth_version', 'wifi_version', 'chipset',
                        'ram_gb', 'storage_gb', 'display_size_inch', 'display_type',
                        'refresh_rate_hz', 'battery_mah', 'fast_charging_w', 'rear_camera_mp',
                        'front_camera_mp', 'camera_setup', 'weight_g', 'thickness_mm'
                    ]
                    
                    data = {
                        "brand": brand, "model_name": model_name, "os": os_type, "launch_year": launch_year,
                        "5g_support": 1 if support_5g == "Yes" else 0,
                        "dual_sim": 1 if dual_sim == "Yes" else 0,
                        "expandable_storage": 1 if expandable_storage == "Yes" else 0,
                        "water_resistance": 1 if water_resistance == "Yes" else 0,
                        "wireless_charging": 1 if wireless_charging == "Yes" else 0,
                        "fingerprint_sensor": 1 if fingerprint_sensor == "Yes" else 0,
                        "face_unlock": 1 if face_unlock == "Yes" else 0,
                        "gpu_score": gpu_score, "cpu_score": cpu_score,
                        "screen_to_body_ratio": screen_to_body_ratio, "build_material": build_material,
                        "colors_available": colors_available, "warranty_years": warranty_years,
                        "bluetooth_version": bluetooth_version, "wifi_version": wifi_version, "chipset": chipset,
                        "ram_gb": ram_gb, "storage_gb": storage_gb, "display_size_inch": display_size_inch,
                        "display_type": display_type, "refresh_rate_hz": refresh_rate_hz, "battery_mah": battery_mah,
                        "fast_charging_w": fast_charging_w, "rear_camera_mp": rear_camera_mp,
                        "front_camera_mp": front_camera_mp, "camera_setup": camera_setup, "weight_g": weight_g,
                        "thickness_mm": thickness_mm
                    }
                    
                    df = pd.DataFrame([data], columns=expected_features)
                    try:
                        prediction_encoded = model.predict(df)
                        predicted_class = le.inverse_transform(prediction_encoded)[0]
                        
                        price_range = predicted_class
                        if '(' in predicted_class and ')' in predicted_class:
                            range_part = predicted_class.split('(')[1].split(')')[0]
                            price_range = range_part.replace('INR', '').strip()
                            try:
                                parts = [p.strip() for p in price_range.split('-')]
                                formatted = []
                                for p in parts:
                                    if p.upper().endswith('K'):
                                        val = int(p[:-1]) * 1000
                                        formatted.append(f'₹{val:,}')
                                    else:
                                        formatted.append(p)
                                price_range = ' - '.join(formatted)
                            except:
                                pass
                                
                        st.success("### Predicted Price Range")
                        st.markdown(f"# {price_range}")
                        st.info(f"**Category:** {predicted_class}")
                        
                        insert_search_history("Current Price", brand, model_name, price_range)
                    except Exception as e:
                        st.error(f"Error predicting: {e}")
