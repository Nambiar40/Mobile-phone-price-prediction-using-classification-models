from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os
import sklearn
import re
import pytesseract
import cv2
from PIL import Image
from pyzbar.pyzbar import decode
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import threading

# --- Database Initialization ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'history.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_type TEXT,
                brand TEXT,
                model_name TEXT,
                predicted_price TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT,
                email TEXT UNIQUE,
                password TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS price_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                platform TEXT,
                product_name TEXT,
                target_price REAL,
                current_price REAL,
                image_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_checked DATETIME
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                type TEXT,
                read_status BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

# Set Tesseract path (Windows typically installs it here)
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
elif os.path.exists(r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
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

app = Flask(__name__)
CORS(app)  # allows your frontend (different port) to call this API

# -- Load the Random Forest Classifier model --
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
    raise FileNotFoundError(f"Could not find resale price model bundle in any of: {POSSIBLE_PATHS}")

print(f"Loading resale model bundle from: {bundle_path}")
bundle = joblib.load(bundle_path)
model = bundle['model']
encoders = bundle['encoders']
band_ranges = bundle['band_ranges']
band_names = bundle.get('band_names', {})
feature_columns = bundle['feature_columns']
categorical_columns = bundle['categorical_columns']
engineered_features = bundle.get('engineered_features', [])
metrics = bundle.get('metrics', {})

print(f"Model type: {bundle.get('model_type', 'Unknown')}")
print(f"Model accuracy: {metrics.get('accuracy', 'N/A')}")
print(f"Price bands: {len(band_ranges)}")

# -- Load Current Price model --
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
        print(f"Loading current price model from: {cp}")
        current_model = joblib.load(cp)
        patch_sklearn_objects(current_model)
        break

for cep in CURRENT_ENCODER_PATHS:
    if os.path.exists(cep):
        print(f"Loading current price encoder from: {cep}")
        current_label_encoder = joblib.load(cep)
        break

if current_model is None:
    print(f"WARNING: Current price model not found in: {CURRENT_MODEL_PATHS}")
if current_label_encoder is None:
    print(f"WARNING: Current price label encoder not found in: {CURRENT_ENCODER_PATHS}")

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
    """Ensure the model name, OS, and chipset align with the major brand."""
    if not brand:
        return None
    
    brand_lower = brand.strip().lower()
    
    # 1. Model Name Validation
    if model_name:
        model_lower = model_name.strip().lower()
        for correct_brand, patterns in BRAND_PATTERNS.items():
            if brand_lower == correct_brand.lower():
                continue
                
            for pat in patterns:
                if re.search(pat, model_lower):
                    return f"Model name '{model_name}' appears to be a {correct_brand} device, but brand '{brand}' was selected."

    # 2. Operating System Validation
    if os_name:
        os_lower = os_name.strip().lower()
        if brand_lower == 'apple' and os_lower not in ['ios', 'ipados', 'mac os', 'macos', 'other']:
            return f"Apple devices run iOS/iPadOS, but OS '{os_name}' was selected."
        elif brand_lower != 'apple' and os_lower in ['ios', 'ipados']:
            return f"Only Apple devices run iOS, but brand '{brand}' was selected."

    # 3. Chipset Validation
    if chipset:
        chipset_lower = chipset.strip().lower()
        
        # Apple Silicon keywords
        apple_chip_patterns = [r'\bbionic\b', r'\bapple\b', r'\ba\d{2}\b', r'\bm\d\b']
        is_apple_chip = any(re.search(pat, chipset_lower) for pat in apple_chip_patterns)
        
        if brand_lower == 'apple' and not is_apple_chip:
            return f"Apple devices use Apple Silicon (A-series/M-series/Bionic), but chipset '{chipset}' was entered."
        elif brand_lower != 'apple' and is_apple_chip:
            return f"Apple Silicon is exclusive to Apple, but brand '{brand}' was selected with chipset '{chipset}'."
            
        # Google Tensor keywords
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
    """Encode a value with a LabelEncoder; fall back to the most common
    training class if the value was never seen during training, instead
    of crashing the request."""
    if value in le.classes_:
        return le.transform([value])[0], None
    fallback = le.classes_[0]
    warning = f"Unrecognized {field_name} '{value}' - used '{fallback}' as a substitute for prediction."
    return le.transform([fallback])[0], warning


def compute_engineered_features(row):
    """Compute the engineered features that were used during training.
    These must match exactly what the training script produced."""
    # depreciation_pct: we don't have resale_price at prediction time,
    # so we estimate it using age and condition as proxy
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
    processor = row.get('processor_score', 50000)
    camera = row.get('camera_score', 70)
    box = row.get('box_available', 1)
    charger = row.get('charger_available', 1)

    # Estimate depreciation % based on age and condition factors
    base_dep = min(age * 2.5, 70)  # ~2.5% per month, max 70%
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


# Total number of bands (used to detect the ceiling band)
TOTAL_BANDS = len(band_ranges)


def estimate_resale_range(band_label, band_ranges, row_data):
    """Compute a specific estimated price range within the predicted band.
    Uses depreciation logic to find a point estimate, then builds a
    ±10% window around it, clipped to the band's boundaries.
    This ensures every phone gets a unique, realistic range.
    """
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

    # --- Depreciation model ---
    # Base: ~2.5% per month, slowing after 24 months
    if age <= 24:
        base_dep = age * 2.5
    else:
        base_dep = 24 * 2.5 + (age - 24) * 1.0   # slower after 2 years
    base_dep = min(base_dep, 75)

    # Condition penalties
    condition_penalty = (
        screen_cracked * 12
        + body_damage * 8
        + water_damage * 18
        + repair_history * 6
    )
    battery_penalty = max(0, (100 - battery_health) * 0.6)

    # Positive adjustments
    bonus = has_5g * 2 + (warranty / 12) * 1.5 + box * 1 + charger * 0.5

    total_dep = min(base_dep + condition_penalty + battery_penalty - bonus, 85)
    total_dep = max(total_dep, 5)   # minimum 5% depreciation

    estimated_value = int(original * (1 - total_dep / 100))

    # Build ±10% window around estimate
    margin = int(estimated_value * 0.10)
    range_low  = max(b_low, estimated_value - margin)
    range_high = min(b_high, estimated_value + margin)

    # Cap top band at 90% of original price
    if band_label == TOTAL_BANDS - 1:
        max_resale = int(original * 0.90)
        range_high = min(range_high, max_resale)

    # Ensure range_low < range_high
    if range_low >= range_high:
        range_low = max(b_low, range_high - int(range_high * 0.10))

    return range_low, range_high


@app.route('/predict-resale', methods=['POST'])
def predict_resale():
    try:
        data = request.get_json()
        
        # Specs Validation
        brand = data.get('brand')
        model_name = data.get('model_name') or data.get('model', '')
        os_name = data.get('os', '') or data.get('os_type', '')
        chipset = data.get('chipset', '')
        
        if brand:
            val_error = validate_device_specs(brand, model_name, os_name, chipset)
            if val_error:
                return jsonify({'success': False, 'error': val_error}), 400

        warnings = []

        row = {}
        # Collect base features from request
        base_features = [f for f in feature_columns if f not in engineered_features]
        for col in base_features:
            if col not in data:
                return jsonify({'success': False, 'error': f'Missing field: {col}'}), 400
            row[col] = data[col]

        # Normalize city_tier (int -> "TierN" string)
        row['city_tier'] = normalize_city_tier(row['city_tier'])

        # Normalize seller_type ("Dealer" -> "Store")
        row['seller_type'] = SELLER_TYPE_MAP.get(row['seller_type'], row['seller_type'])

        # Encode all categorical fields safely
        for col, le in encoders.items():
            encoded_val, warning = safe_encode(le, row[col], col)
            row[col] = encoded_val
            if warning:
                warnings.append(warning)

        # Compute engineered features
        row = compute_engineered_features(row)

        # Build DataFrame in the exact column order used during training
        input_df = pd.DataFrame([row])[feature_columns]

        # Predict price band (Classifier)
        predicted_band = model.predict(input_df)[0]
        proba = model.predict_proba(input_df)[0]
        confidence = float(np.max(proba))

        # Get price range for predicted band
        low, high = band_ranges[predicted_band]
        band_name = band_names.get(predicted_band, f"Band {predicted_band}")

        # Get top 3 predictions
        original_price = data.get('original_price', None)

        top_3_indices = np.argsort(proba)[::-1][:3]
        top_3 = []
        for idx in top_3_indices:
            band_label = model.classes_[idx]
            if band_label in band_ranges:
                r_low, r_high = estimate_resale_range(band_label, band_ranges, data)
                top_3.append({
                    'band': int(band_label),
                    'name': f"Rs.{r_low:,} - Rs.{r_high:,}",
                    'range': f"Rs.{r_low:,} - Rs.{r_high:,}",
                    'probability': round(float(proba[idx]) * 100, 1)
                })

        # Main prediction range — narrow estimate within the band
        est_low, est_high = estimate_resale_range(predicted_band, band_ranges, data)
        display_range = f"Rs.{est_low:,} - Rs.{est_high:,}"

        # Save to History DB
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO search_history (prediction_type, brand, model_name, predicted_price)
                    VALUES (?, ?, ?, ?)
                ''', ('Resale Price', brand or 'Unknown', model_name or 'Unknown', display_range))
                conn.commit()
        except Exception as db_e:
            db_error_msg = f"DB Error (Resale): {str(db_e)}"
            print(db_error_msg)
            warnings.append(db_error_msg)

        return jsonify({
            'success': True,
            'price_range': display_range,
            'prediction': display_range,
            'band_name': band_name,
            'confidence': round(confidence * 100, 1),
            'band': int(predicted_band),
            'top_predictions': top_3,
            'model_accuracy': round(float(metrics.get('accuracy', 0)) * 100, 1),
            'within_1_band': round(float(metrics.get('within_1_band', 0)) * 100, 1),
            'warnings': warnings
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/predict-current-price', methods=['POST'])
def predict_current_price():
    if current_model is None or current_label_encoder is None:
        return jsonify({
            'success': False,
            'error': 'Current price model files are not loaded. Run ml/current/train_model.py first.'
        }), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided.'}), 400

        # Specs Validation
        brand = data.get('brand')
        model_name = data.get('model_name', '')
        os_name = data.get('os', '')
        chipset = data.get('chipset', '')
        
        if brand:
            val_error = validate_device_specs(brand, model_name, os_name, chipset)
            if val_error:
                return jsonify({'success': False, 'error': val_error}), 400

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

        missing = [f for f in expected_features if f not in data]
        if missing:
            return jsonify({'success': False, 'error': f'Missing fields: {missing}'}), 400

        # Convert Yes/No boolean fields to 1/0
        boolean_fields = [
            '5g_support', 'dual_sim', 'expandable_storage', 'water_resistance',
            'wireless_charging', 'fingerprint_sensor', 'face_unlock'
        ]
        for field in boolean_fields:
            if field in data and isinstance(data[field], str):
                data[field] = 1 if data[field].lower() == 'yes' else 0

        df = pd.DataFrame([data], columns=expected_features)
        prediction_encoded = current_model.predict(df)
        predicted_class = current_label_encoder.inverse_transform(prediction_encoded)[0]

        # Format the price range for display
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

        # Save to History DB
        db_warning = None
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO search_history (prediction_type, brand, model_name, predicted_price)
                    VALUES (?, ?, ?, ?)
                ''', ('Current Price', brand or 'Unknown', model_name or 'Unknown', price_range))
                conn.commit()
        except Exception as db_e:
            db_warning = f"DB Error (Current Price): {str(db_e)}"
            print(db_warning)

        response_data = {'success': True, 'predicted_class': predicted_class, 'price_range': price_range}
        if db_warning:
            response_data['warning'] = db_warning
            
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(BASE_DIR, path)):
        return send_from_directory(BASE_DIR, path)
    return jsonify({'error': '404 Not Found'}), 404

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    password = data.get('password')
    
    if not all([fullname, email, password]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
    try:
        hashed_password = generate_password_hash(password)
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)', 
                     (fullname, email, hashed_password))
            conn.commit()
        return jsonify({'success': True, 'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Email already registered'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            
        if user and check_password_hash(user[3], password):
            return jsonify({'success': True, 'message': 'Login successful', 'fullname': user[1]})
        else:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, prediction_type, brand, model_name, predicted_price, timestamp FROM search_history ORDER BY timestamp DESC LIMIT 50')
            rows = c.fetchall()
        
        history = []
        for r in rows:
            history.append({
                'id': r[0],
                'type': r[1],
                'brand': r[2],
                'model_name': r[3],
                'price': r[4],
                'date': r[5]
            })
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ocr-extract', methods=['POST'])
def ocr_extract():
    if 'invoice_image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
        
    file = request.files['invoice_image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No image file selected'}), 400
        
    try:
        # Read the image file using OpenCV
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'success': False, 'error': 'Could not decode image'}), 400
            
        # Preprocessing to improve OCR accuracy
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Optional: Thresholding or resizing could be added here if needed
        # _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Run Tesseract OCR
        text = pytesseract.image_to_string(gray)
        
        # Run pyzbar to find barcodes/QR codes
        barcodes = decode(img)
        barcode_data_list = []
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            barcode_data_list.append(f"[{barcode_type}] {barcode_data}")
            # If the barcode has text, append it to the OCR text for parsing
            text += f"\nBARCODE_CONTENT: {barcode_data}"
            
        # --- Parsing Logic ---
        # Initialize extracted variables
        extracted_data = {
            'brand': '',
            'model': '',
            'original_price': '',
            'purchase_year': '',
            'barcode': ', '.join(barcode_data_list) if barcode_data_list else ''
        }
        
        # Known brands for matching
        known_brands = ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Vivo', 'Oppo', 'Realme', 'Motorola', 'Nothing']
        
        # Try to find Brand
        text_lower = text.lower()
        for brand in known_brands:
            if brand.lower() in text_lower:
                extracted_data['brand'] = brand
                break
                
        # Try to find Model (Look for "Model" followed by text)
        model_match = re.search(r'model[\s:]+([A-Za-z0-9\s-]+)', text, re.IGNORECASE)
        if model_match:
            # Clean up the model string (stop at newline or long spaces)
            model_str = model_match.group(1).split('\n')[0].strip()
            # Remove any trailing commas or random chars
            model_str = re.sub(r'[,|\|]', '', model_str).strip()
            extracted_data['model'] = model_str
            
        # Try to find Price (Look for Rs. or ₹ or Price followed by numbers)
        # e.g., Rs. 72,999 or Price: 72999
        price_match = re.search(r'(?:rs\.?|₹|price)[\s:]*([\d,]+(?:\.\d{2})?)', text, re.IGNORECASE)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            try:
                extracted_data['original_price'] = float(price_str)
            except ValueError:
                pass
                
        # Try to find Date/Year (Look for YYYY-MM-DD or DD/MM/YYYY or just a 202x year)
        # First, try to find a year with clear context
        year_match = re.search(r'(?:year|mfg|date|purchase|bill)[\s:-]*(20[1-2][0-9])', text, re.IGNORECASE)
        
        if not year_match:
            # Fallback: look for a year, but ignore lines that look like camera watermarks 
            # (e.g. "Shot on OnePlus", or lines with timestamps like "2026.08.31" or "|")
            lines = text.split('\n')
            valid_lines = [
                l for l in lines 
                if not re.search(r'(?i)shot on', l) 
                and not re.search(r'20\d\d[\./-]\d\d[\./-]\d\d', l)
                and '|' not in l
            ]
            for line in valid_lines:
                ym = re.search(r'\b(20[1-2][0-9])\b', line)
                if ym:
                    year_match = ym
                    break

        if year_match:
            extracted_data['purchase_year'] = int(year_match.group(1))
            
        # Save to History DB
        try:
            price_val = extracted_data.get('original_price', '')
            price_display = f"Rs.{price_val}" if price_val else "N/A"
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO search_history (prediction_type, brand, model_name, predicted_price)
                    VALUES (?, ?, ?, ?)
                ''', ('OCR Scan', extracted_data.get('brand') or 'Unknown', extracted_data.get('model') or 'Unknown', price_display))
                conn.commit()
        except Exception as db_e:
            print(f"DB Error (OCR Scan): {str(db_e)}")
            
        return jsonify({
            'success': True,
            'raw_text': text,
            'extracted_data': extracted_data
        })
        
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# --- Price Tracker Logic ---

def scrape_amazon_price(url):
    """Scrapes Amazon for product name, price, and image using basic headers."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url} (Status: {response.status_code})")
            return None, None, None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find(id='productTitle')
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"
        
        # Extract price (Amazon changes classes frequently, trying common ones)
        price_tag = soup.find('span', {'class': 'a-price-whole'})
        if not price_tag:
            price_tag = soup.find('span', {'id': 'priceblock_ourprice'})
        
        price = None
        if price_tag:
            price_str = price_tag.get_text(strip=True).replace(',', '').replace('₹', '').replace('.', '')
            try:
                price = float(price_str)
            except ValueError:
                pass
                
        # Extract image
        img_tag = soup.find(id='landingImage')
        img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ""
        
        return title, price, img_url
        
    except Exception as e:
        print(f"Scraping error: {str(e)}")
        return None, None, None

def background_price_check():
    """Function to run periodically to check tracked prices."""
    print(f"[{datetime.datetime.now()}] Running background price check...")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, url, product_name, target_price, current_price FROM price_tracker WHERE is_active = 1')
            items = c.fetchall()
            
            for item in items:
                item_id, url, name, target_price, old_price = item
                
                title, new_price, _ = scrape_amazon_price(url)
                
                if new_price is not None:
                    # Update DB
                    c.execute('UPDATE price_tracker SET current_price = ?, last_checked = CURRENT_TIMESTAMP WHERE id = ?', (new_price, item_id))
                    
                    # Check for price drop
                    if old_price is None or new_price < old_price:
                        if target_price and new_price <= target_price:
                            msg = f"TARGET REACHED: {name} dropped to ₹{new_price} (Target: ₹{target_price})"
                            c.execute('INSERT INTO notifications (message, type) VALUES (?, ?)', (msg, 'success'))
                        else:
                            msg = f"PRICE DROP: {name} is now ₹{new_price} (was ₹{old_price})"
                            c.execute('INSERT INTO notifications (message, type) VALUES (?, ?)', (msg, 'info'))
            
            conn.commit()
    except Exception as e:
        print(f"Background check error: {str(e)}")

# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=background_price_check, trigger="interval", hours=4)
scheduler.start()

# --- Price Tracker API Endpoints ---

@app.route('/api/track-price', methods=['POST'])
def add_tracked_item():
    data = request.get_json()
    url = data.get('url')
    target_price_str = data.get('target_price', '')
    
    url_lower = url.lower()
    if 'amazon' not in url_lower and 'amzn.in' not in url_lower and 'amzn.to' not in url_lower:
        return jsonify({'success': False, 'error': 'Currently, only Amazon URLs (including amzn.in or amzn.to) are supported.'}), 400
        
    try:
        target_price = float(target_price_str) if target_price_str else None
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid target price format.'}), 400
        
    title, price, img_url = scrape_amazon_price(url)
    
    if not title or price is None:
        return jsonify({'success': False, 'error': 'Failed to fetch product details from Amazon. The URL might be invalid or Amazon blocked the request.'}), 400
        
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO price_tracker (url, platform, product_name, target_price, current_price, image_url, last_checked)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (url, 'Amazon', title, target_price, price, img_url))
            conn.commit()
            
            # Create a success notification
            c.execute('INSERT INTO notifications (message, type) VALUES (?, ?)', (f"Started tracking {title[:30]}... at ₹{price}", 'info'))
            
            # Also log to search history
            price_display = f"Rs.{price}" if price else "N/A"
            c.execute('''
                INSERT INTO search_history (prediction_type, brand, model_name, predicted_price)
                VALUES (?, ?, ?, ?)
            ''', ('Price Tracker', 'Amazon', title[:50] + ('...' if len(title) > 50 else ''), price_display))
            
            conn.commit()
            
        return jsonify({'success': True, 'message': 'Product added to tracker!', 'product': {'name': title, 'price': price}})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'This URL is already being tracked.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tracked-prices', methods=['GET'])
def get_tracked_items():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, url, platform, product_name, target_price, current_price, image_url, last_checked FROM price_tracker WHERE is_active = 1 ORDER BY created_at DESC')
            rows = c.fetchall()
            
        items = []
        for r in rows:
            items.append({
                'id': r[0],
                'url': r[1],
                'platform': r[2],
                'name': r[3],
                'target_price': r[4],
                'current_price': r[5],
                'image_url': r[6],
                'last_checked': r[7]
            })
        return jsonify({'success': True, 'items': items})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/delete-tracked-price/<int:item_id>', methods=['DELETE'])
def delete_tracked_item(item_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM price_tracker WHERE id = ?', (item_id,))
            conn.commit()
        return jsonify({'success': True, 'message': 'Item removed from tracker.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, message, type, created_at FROM notifications WHERE read_status = 0 ORDER BY created_at DESC LIMIT 20')
            rows = c.fetchall()
            
        notifications = []
        for r in rows:
            notifications.append({
                'id': r[0],
                'message': r[1],
                'type': r[2],
                'created_at': r[3]
            })
        return jsonify({'success': True, 'notifications': notifications})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    try:
        data = request.get_json()
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({'success': True})
            
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            c.execute(f'UPDATE notifications SET read_status = 1 WHERE id IN ({placeholders})', ids)
            conn.commit()
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
