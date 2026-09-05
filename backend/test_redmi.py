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

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'models', 'current_price_model.pkl')
encoder_path = os.path.join(base_dir, 'models', 'current_price_label_encoder.pkl')

model = joblib.load(model_path)
patch_sklearn_objects(model)
label_encoder = joblib.load(encoder_path)

print("Model Type:", type(model))
expected_features = list(model.steps[0][1].feature_names_in_)

sample_data = {
    'brand': "Xiaomi", 'model_name': "Redmi 12", 'os': "Android", 'launch_year': 2023, 
    '5g_support': 0, 'dual_sim': 1, 'expandable_storage': 1, 
    'water_resistance': 0, 'wireless_charging': 0, 'fingerprint_sensor': 1, 
    'face_unlock': 1, 'gpu_score': 25000, 'cpu_score': 60000, 
    'screen_to_body_ratio': 85.1, 'build_material': "Plastic", 'colors_available': 3, 
    'warranty_years': 1, 'bluetooth_version': 5.3, 'wifi_version': 5, 
    'chipset': "MediaTek Helio G88", 'ram_gb': 4, 'storage_gb': 128, 'display_size_inch': 6.79, 
    'display_type': "IPS LCD", 'refresh_rate_hz': 90, 'battery_mah': 5000, 
    'fast_charging_w': 18, 'rear_camera_mp': 50, 'front_camera_mp': 8, 
    'camera_setup': "Triple", 'weight_g': 198, 'thickness_mm': 8.2
}

df = pd.DataFrame([sample_data], columns=expected_features)

print("\n--- Making Prediction ---")
pred_encoded = model.predict(df)
pred_class = label_encoder.inverse_transform(pred_encoded)[0]
print(f"Predicted Class: {pred_class}")

# Let's inspect the pipeline steps
print("\n--- Pipeline Steps ---")
for name, step in model.steps:
    print(f"Step: {name}, {type(step)}")

classifier = model.steps[-1][1]
if hasattr(classifier, 'feature_importances_'):
    print("\n--- Feature Importances ---")
    importances = classifier.feature_importances_
    # Try to get feature names after preprocessing
    try:
        preprocessor = model.steps[0][1]
        feature_names = preprocessor.get_feature_names_out()
        imp_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
        print(imp_df.sort_values(by='importance', ascending=False).head(15))
    except Exception as e:
        print(f"Could not get feature names: {e}")
        # Print top indices
        import numpy as np
        top_indices = np.argsort(importances)[::-1][:15]
        print(f"Top feature indices: {top_indices}")
