import os
import joblib
import pandas as pd
import sklearn

# Patch sklearn.compose._column_transformer for compatibility
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

def main():
    print("Testing Model Loading and Prediction...\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, 'models')
    model_path = os.path.join(model_dir, 'current_price_model.pkl')
    encoder_path = os.path.join(model_dir, 'current_price_label_encoder.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        print(f"Error: .pkl files not found in {model_dir}")
        print("Please copy current_price_model.pkl and current_price_label_encoder.pkl into backend/models/")
        return

    try:
        print(f"Loading model from {model_path}...")
        model = joblib.load(model_path)
        patch_sklearn_objects(model)
        print("Model loaded successfully.")
        
        print(f"Loading label encoder from {encoder_path}...")
        label_encoder = joblib.load(encoder_path)
        print("Label encoder loaded successfully.")
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    print(f"Model type: {type(model)}")
    
    # Get expected features
    if hasattr(model, 'feature_names_in_'):
        expected_features = list(model.feature_names_in_)
    else:
        # Fallback if it's a pipeline
        expected_features = list(model.steps[0][1].feature_names_in_)
        
    print(f"Expected features ({len(expected_features)}): {expected_features}\n")
    
    # Create a valid sample input
    print("Creating sample input...")
    sample_data = {
        'brand': "Apple",
        'model_name': "iPhone 13",
        'os': "iOS",
        'launch_year': 2021,
        '5g_support': "Yes",
        'dual_sim': "Yes",
        'expandable_storage': "No",
        'water_resistance': "Yes",
        'wireless_charging': "Yes",
        'fingerprint_sensor': "No",
        'face_unlock': "Yes",
        'gpu_score': 85000,
        'cpu_score': 95000,
        'screen_to_body_ratio': 86.0,
        'build_material': "Glass",
        'colors_available': 5,
        'warranty_years': 1,
        'bluetooth_version': 5.0,
        'wifi_version': 6,
        'chipset': "A15 Bionic",
        'ram_gb': 4,
        'storage_gb': 128,
        'display_size_inch': 6.1,
        'display_type': "OLED",
        'refresh_rate_hz': 60,
        'battery_mah': 3240,
        'fast_charging_w': 20,
        'rear_camera_mp': 12,
        'front_camera_mp': 12,
        'camera_setup': "Dual",
        'weight_g': 174,
        'thickness_mm': 7.6
    }
    
    # Convert Yes/No to 1/0 for boolean fields
    boolean_fields = [
        '5g_support', 'dual_sim', 'expandable_storage', 'water_resistance', 
        'wireless_charging', 'fingerprint_sensor', 'face_unlock'
    ]
    for field in boolean_fields:
        if isinstance(sample_data[field], str):
            sample_data[field] = 1 if sample_data[field].lower() == 'yes' else 0
            
    # Convert to DataFrame
    df = pd.DataFrame([sample_data], columns=expected_features)
    
    print("Making prediction...")
    try:
        prediction_encoded = model.predict(df)
        print(f"Encoded prediction: {prediction_encoded[0]}")
        
        predicted_class = label_encoder.inverse_transform(prediction_encoded)[0]
        print(f"Predicted class: {predicted_class}")
        
        # Try to parse price range
        price_range = predicted_class
        if "(" in predicted_class and ")" in predicted_class:
            range_part = predicted_class.split("(")[1].split(")")[0].replace("INR", "").strip()
            print(f"Price range: {range_part}")
            
    except Exception as e:
        print(f"Prediction error: {e}")

if __name__ == "__main__":
    main()
