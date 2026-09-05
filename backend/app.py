import os
import sys
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import sklearn

# Patch sklearn.compose._column_transformer for compatibility with older models
if not hasattr(sklearn.compose._column_transformer, '_RemainderColsList'):
    class _RemainderColsList(list):
        pass
    sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

def patch_sklearn_objects(obj):
    if hasattr(obj, 'steps'):
        for name, step in obj.steps:
            patch_sklearn_objects(step)
            
    if hasattr(obj, 'transformers_'):
        for name, transformer, cols in obj.transformers_:
            patch_sklearn_objects(transformer)
    elif hasattr(obj, 'transformers'):
        for name, transformer, cols in obj.transformers:
            patch_sklearn_objects(transformer)
            
    if type(obj).__name__ == 'SimpleImputer':
        if not hasattr(obj, '_fill_dtype'):
            import numpy as np
            if hasattr(obj, 'statistics_') and obj.statistics_ is not None:
                obj._fill_dtype = obj.statistics_.dtype
            else:
                obj._fill_dtype = np.dtype('object') if getattr(obj, 'strategy', '') == 'most_frequent' else np.dtype('float64')

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Get the absolute path to the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the models folder
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'current_price_model.pkl')
ENCODER_PATH = os.path.join(MODEL_DIR, 'current_price_label_encoder.pkl')

model = None
label_encoder = None

def load_models():
    global model, label_encoder
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
            model = joblib.load(MODEL_PATH)
            patch_sklearn_objects(model)
            label_encoder = joblib.load(ENCODER_PATH)
            print("Models loaded successfully.")
        else:
            print(f"Warning: Models not found at {MODEL_DIR}. Please place them there.")
    except Exception as e:
        print(f"Error loading models: {e}")

load_models()

@app.route('/predict-current-price', methods=['POST'])
def predict_current_price():
    if model is None or label_encoder is None:
        return jsonify({
            "success": False,
            "error": "Model files are not loaded. Please make sure .pkl files are in the backend/models directory."
        }), 500

    try:
        # Get JSON data from frontend
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        # Expected features based on model inspection
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

        # Check for missing features
        missing_features = [feature for feature in expected_features if feature not in data]
        if missing_features:
            return jsonify({
                "success": False, 
                "error": f"Missing expected features: {', '.join(missing_features)}"
            }), 400

        # Convert Yes/No to 1/0 for boolean fields that the pipeline expects as numeric
        boolean_fields = [
            '5g_support', 'dual_sim', 'expandable_storage', 'water_resistance', 
            'wireless_charging', 'fingerprint_sensor', 'face_unlock'
        ]
        for field in boolean_fields:
            if field in data and isinstance(data[field], str):
                data[field] = 1 if data[field].lower() == 'yes' else 0

        # Convert the received data into a pandas DataFrame using the exact expected features order
        df = pd.DataFrame([data], columns=expected_features)

        # Make prediction directly with the pipeline (handles preprocessing)
        prediction_encoded = model.predict(df)

        # Decode the prediction using the saved label encoder
        predicted_class = label_encoder.inverse_transform(prediction_encoded)[0]

        # Extract numerical range if it's formatted as "Category (Min - Max INR)"
        price_range = predicted_class
        if "(" in predicted_class and ")" in predicted_class:
            range_part = predicted_class.split("(")[1].split(")")[0]
            # Try to format it slightly better, e.g., "35K - 60K INR" to "₹35,000 - ₹60,000"
            price_range = range_part.replace("INR", "").strip()
            
            # Basic parsing if format is e.g. "35K - 60K"
            try:
                parts = [p.strip() for p in price_range.split("-")]
                formatted_parts = []
                for p in parts:
                    if p.upper().endswith("K"):
                        val = int(p[:-1]) * 1000
                        formatted_parts.append(f"₹{val:,}")
                    else:
                        formatted_parts.append(p)
                price_range = " - ".join(formatted_parts)
            except:
                pass # Fallback to original string

        return jsonify({
            "success": True,
            "predicted_class": predicted_class,
            "price_range": price_range
        })

    except Exception as e:
        # Handle exceptions gracefully and return error to frontend
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
