import os
import joblib
import pandas as pd
import numpy as np
import sklearn
import re
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -- sklearn compatibility patch for older pipeline models --
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
            if hasattr(obj, 'statistics_') and obj.statistics_ is not None:
                obj._fill_dtype = obj.statistics_.dtype
            else:
                obj._fill_dtype = np.dtype('object') if getattr(obj, 'strategy', '') == 'most_frequent' else np.dtype('float64')

@st.cache_resource
def load_resale_model():
    POSSIBLE_PATHS = [
        os.path.join(BASE_DIR, 'ml', 'resale', 'resale_price_rf_classifier.pkl'),
        os.path.join(BASE_DIR, 'resale_price_rf_classifier.pkl'),
    ]
    bundle_path = None
    for p in POSSIBLE_PATHS:
        if os.path.exists(p):
            bundle_path = p
            break
            
    if not bundle_path:
        st.error(f"Could not find resale price model bundle in any of: {POSSIBLE_PATHS}")
        return None
        
    bundle = joblib.load(bundle_path)
    return bundle

@st.cache_resource
def load_current_price_model():
    CURRENT_MODEL_PATHS = [
        os.path.join(BASE_DIR, 'backend', 'models', 'current_price_model.pkl'),
        os.path.join(BASE_DIR, 'ml', 'current', 'current_price_model.pkl'),
    ]
    CURRENT_ENCODER_PATHS = [
        os.path.join(BASE_DIR, 'backend', 'models', 'current_price_label_encoder.pkl'),
        os.path.join(BASE_DIR, 'ml', 'current', 'current_price_label_encoder.pkl'),
    ]
    
    current_model = None
    current_label_encoder = None
    
    for cp in CURRENT_MODEL_PATHS:
        if os.path.exists(cp):
            current_model = joblib.load(cp)
            patch_sklearn_objects(current_model)
            break
            
    for cep in CURRENT_ENCODER_PATHS:
        if os.path.exists(cep):
            current_label_encoder = joblib.load(cep)
            break
            
    return current_model, current_label_encoder

# --- Normalization helpers ---
BRAND_PATTERNS = {
    'Apple': [r'\biphone\b', r'\bipad\b', r'\bmac\b'],
    'Samsung': [r'\bgalaxy\b', r'\bz fold\b', r'\bz flip\b', r'\bnote\b', r'\bs\d{2}\b', r'\ba\d{2}\b', r'\bm\d{2}\b', r'\bf\d{2}\b', r'\bj\d{1,2}\b'],
    'Google': [r'\bpixel\b', r'\bnexus\b'],
    'OnePlus': [r'\bnord\b', r'\boneplus\b', r'\bace\b'],
    'Motorola': [r'\bmoto\b', r'\brazr\b', r'\bedge\b', r'\bg\d{1,3}\b', r'\be\d{1,2}\b', r'\bdefy\b'],
    'Nothing': [r'\bnothing\b', r'\bphone\s*\(?[12a]+\)?\b', r'\bcmf\b'],
    'Xiaomi': [r'\bredmi\b', r'\bpoco\b', r'\bxiaomi\b', r'\bblack shark\b', r'\bk\d{2}i?\b', r'\b(?:xiaomi\s+)?mi\b'],
    'Vivo': [r'\bvivo\b', r'\biqoo\b', r'\bnex\b', r'\bx\d{2,3}\b', r'\by\d{2}\b', r'\bv\d{2,3}\b', r'\bt\d\b'],
    'Oppo': [r'\boppo\b', r'\breno\b', r'\bfind\b', r'\bf\d{1,2}\b', r'\bk\d{1,2}\b'],
    'Realme': [r'\brealme\b', r'\bnarzo\b', r'\bgt\b', r'\bc\d{1,2}\b']
}

def validate_device_specs(brand, model_name=None, os_name=None, chipset=None):
    if not brand:
        return None
    brand_lower = brand.strip().lower()
    
    if model_name:
        model_lower = model_name.strip().lower()
        for correct_brand, patterns in BRAND_PATTERNS.items():
            if brand_lower == correct_brand.lower():
                continue
            for pat in patterns:
                if re.search(pat, model_lower):
                    return f"Model name '{model_name}' appears to be a {correct_brand} device, but brand '{brand}' was selected."

    if os_name:
        os_lower = os_name.strip().lower()
        if brand_lower == 'apple' and os_lower not in ['ios', 'ipados', 'mac os', 'macos', 'other']:
            return f"Apple devices run iOS/iPadOS, but OS '{os_name}' was selected."
        elif brand_lower != 'apple' and os_lower in ['ios', 'ipados']:
            return f"Only Apple devices run iOS, but brand '{brand}' was selected."

    if chipset:
        chipset_lower = chipset.strip().lower()
        apple_chip_patterns = [r'\bbionic\b', r'\bapple\b', r'\ba\d{2}\b', r'\bm\d\b']
        is_apple_chip = any(re.search(pat, chipset_lower) for pat in apple_chip_patterns)
        
        if brand_lower == 'apple' and not is_apple_chip:
            return f"Apple devices use Apple Silicon (A-series/M-series/Bionic), but chipset '{chipset}' was entered."
        elif brand_lower != 'apple' and is_apple_chip:
            return f"Apple Silicon is exclusive to Apple, but brand '{brand}' was selected with chipset '{chipset}'."
            
        if brand_lower == 'google' and not (re.search(r'\btensor\b', chipset_lower) or re.search(r'\bsnapdragon\b', chipset_lower)):
            return f"Google Pixel devices typically use Tensor or Snapdragon chipsets, but '{chipset}' was entered."
        elif brand_lower != 'google' and re.search(r'\btensor\b', chipset_lower):
            return f"Google Tensor chipsets are exclusive to Google Pixel devices, but brand '{brand}' was selected."
            
    return None

def normalize_city_tier(value):
    return f"Tier{value}"

SELLER_TYPE_MAP = {
    "Individual": "Individual",
    "Store": "Store",
    "Dealer": "Store",
}

def safe_encode(le, value, field_name):
    if value in le.classes_:
        return le.transform([value])[0], None
    fallback = le.classes_[0]
    warning = f"Unrecognized {field_name} '{value}' - used '{fallback}' as a substitute for prediction."
    return le.transform([fallback])[0], warning

def compute_engineered_features(row):
    age = row.get('age_months', 12)
    original = row.get('original_price', 30000)
    battery_health = row.get('battery_health', 80)
    screen_cracked = row.get('screen_cracked', 0)
    body_damage = row.get('body_damage', 0)
    water_damage = row.get('water_damage', 0)
    repair_history = row.get('repair_history', 0)
    usage_hours = row.get('usage_hours_per_day', 4)
    ram = row.get('ram_gb', 4)
    storage = row.get('storage_gb', 64)
    box = row.get('box_available', 1)
    charger = row.get('charger_available', 1)

    base_dep = min(age * 2.5, 70) 
    condition_penalty = screen_cracked * 10 + body_damage * 8 + water_damage * 15 + repair_history * 5
    health_penalty = max(0, (100 - battery_health) * 0.5)
    estimated_dep_pct = min(base_dep + condition_penalty + health_penalty, 90)

    row['depreciation_pct'] = estimated_dep_pct
    row['price_age_ratio'] = original / (age + 1)
    row['condition_score'] = (
        battery_health / 100.0
        - screen_cracked * 0.3
        - body_damage * 0.2
        - water_damage * 0.4
        - repair_history * 0.1
    )
    row['accessories_score'] = box + charger
    row['spec_value'] = original / (ram * storage + 1)
    row['usage_wear'] = age * usage_hours
    row['effective_age'] = age * (1 + (1 - battery_health / 100))
    return row

def estimate_resale_range(band_label, band_ranges, row_data, TOTAL_BANDS):
    b_low, b_high = band_ranges[band_label]
    original = row_data.get('original_price', 30000)
    age = row_data.get('age_months', 12)
    battery_health = row_data.get('battery_health', 80)
    screen_cracked = row_data.get('screen_cracked', 0)
    body_damage = row_data.get('body_damage', 0)
    water_damage = row_data.get('water_damage', 0)
    repair_history = row_data.get('repair_history', 0)
    has_5g = row_data.get('has_5g', 0)
    warranty = row_data.get('warranty_remaining_months', 0)
    box = row_data.get('box_available', 1)
    charger = row_data.get('charger_available', 1)

    if age <= 24:
        base_dep = age * 2.5
    else:
        base_dep = 24 * 2.5 + (age - 24) * 1.0
    base_dep = min(base_dep, 75)

    condition_penalty = (screen_cracked * 12 + body_damage * 8 + water_damage * 18 + repair_history * 6)
    battery_penalty = max(0, (100 - battery_health) * 0.6)
    bonus = has_5g * 2 + (warranty / 12) * 1.5 + box * 1 + charger * 0.5
    total_dep = min(base_dep + condition_penalty + battery_penalty - bonus, 85)
    total_dep = max(total_dep, 5)

    estimated_value = int(original * (1 - total_dep / 100))
    margin = int(estimated_value * 0.10)
    range_low  = max(b_low, estimated_value - margin)
    range_high = min(b_high, estimated_value + margin)

    if band_label == TOTAL_BANDS - 1:
        max_resale = int(original * 0.90)
        range_high = min(range_high, max_resale)

    if range_low >= range_high:
        range_low = max(b_low, range_high - int(range_high * 0.10))

    return range_low, range_high
