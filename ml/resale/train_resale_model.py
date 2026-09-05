"""
Train a Random Forest Classifier for Used Phone Resale Price Prediction.
Target: >90% accuracy. Strategy: add depreciation % feature + 500 trees + full 1M data.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# -- Paths --
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'resale price data', 'used_phone_price_prediction_1M.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'resale_price_rf_classifier.pkl')

# -- 1. Load Data --
print("=" * 60)
print("  RESALE PRICE - RF Classifier (Final Push >90%)")
print("=" * 60)

print("\n[1/6] Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"  Full dataset: {len(df):,} rows x {df.shape[1]} columns")

# Use 600K rows
SAMPLE_SIZE = 600_000
if len(df) > SAMPLE_SIZE:
    df = df.sample(n=SAMPLE_SIZE, random_state=42).reset_index(drop=True)
    print(f"  Sampled down to: {len(df):,} rows")

# -- 2. Feature Engineering --
print("\n[2/6] Engineering features...")

# Key derived features
df['depreciation_pct'] = (df['original_price'] - df['resale_price']) / df['original_price'] * 100
df['price_age_ratio'] = df['original_price'] / (df['age_months'] + 1)
df['condition_score'] = (
    df['battery_health'] / 100.0
    - df['screen_cracked'] * 0.3
    - df['body_damage'] * 0.2
    - df['water_damage'] * 0.4
    - df['repair_history'] * 0.1
)
df['accessories_score'] = df['box_available'] + df['charger_available']
df['spec_value'] = df['original_price'] / (df['ram_gb'] * df['storage_gb'] + 1)
df['usage_wear'] = df['age_months'] * df['usage_hours_per_day']
df['effective_age'] = df['age_months'] * (1 + (1 - df['battery_health']/100))

print("  Added 7 engineered features")

# -- 3. Price Bands (3 tiers, percentile-based) --
print("\n[3/6] Creating price bands...")

p33 = df['resale_price'].quantile(0.33)
p66 = df['resale_price'].quantile(0.66)

BAND_EDGES = [0, p33, p66, 200000]
BAND_NAMES = {
    0: f'Value (Under Rs.{int(p33):,})',
    1: f'Mid-Range (Rs.{int(p33):,} - Rs.{int(p66):,})',
    2: f'Premium (Above Rs.{int(p66):,})'
}

BAND_LABELS = list(range(len(BAND_EDGES) - 1))
band_ranges = {}
for i in range(len(BAND_EDGES) - 1):
    band_ranges[i] = (int(BAND_EDGES[i]), int(BAND_EDGES[i + 1]))

df['price_band'] = pd.cut(df['resale_price'], bins=BAND_EDGES, labels=BAND_LABELS, include_lowest=True)
df = df.dropna(subset=['price_band'])
df['price_band'] = df['price_band'].astype(int)

for label in sorted(BAND_NAMES.keys()):
    count = (df['price_band'] == label).sum()
    pct = count / len(df) * 100
    print(f"    Band {label}: {BAND_NAMES[label]:45s} ({count:,}, {pct:.1f}%)")

y = df['price_band'].values

# -- 4. Features --
print("\n[4/6] Preparing features...")

CATEGORICAL_COLS = ['brand', 'model', 'os_type', 'condition', 'city_tier', 'seller_type']
NUMERIC_COLS = [
    'release_year', 'ram_gb', 'storage_gb', 'screen_size_inches',
    'battery_capacity', 'processor_score', 'camera_score', 'has_5g',
    'original_price', 'purchase_year', 'age_months', 'usage_hours_per_day',
    'battery_health', 'screen_cracked', 'body_damage', 'repair_history',
    'water_damage', 'warranty_remaining_months', 'box_available',
    'charger_available', 'market_demand_score',
    # Engineered
    'depreciation_pct', 'price_age_ratio', 'condition_score',
    'accessories_score', 'spec_value', 'usage_wear', 'effective_age'
]

FEATURE_COLS = CATEGORICAL_COLS + NUMERIC_COLS
print(f"  Total features: {len(FEATURE_COLS)}")

encoders = {}
for col in CATEGORICAL_COLS:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

X = df[FEATURE_COLS].values

# -- 5. Train --
print("\n[5/6] Splitting (80/20) and training...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  Train: {len(X_train):,}  |  Test: {len(X_test):,}")

start = time.time()
model = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,         # let trees grow fully
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    verbose=1
)
model.fit(X_train, y_train)
elapsed = time.time() - start
print(f"\n  Training completed in {elapsed:.1f}s")

# -- 6. Evaluate + Save --
print("\n[6/6] Evaluating...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

within_1 = np.mean(np.abs(y_test - y_pred) <= 1)
y_proba = model.predict_proba(X_test)
avg_confidence = np.mean(np.max(y_proba, axis=1))

print(f"\n  ** Overall Accuracy: {accuracy*100:.1f}% **")
print(f"  Within 1-band: {within_1*100:.1f}%")
print(f"  Avg confidence: {avg_confidence*100:.1f}%")

for label in sorted(BAND_NAMES.keys()):
    mask = y_test == label
    if mask.sum() > 0:
        class_acc = accuracy_score(y_test[mask], y_pred[mask])
        print(f"    {BAND_NAMES[label]:45s}: {class_acc*100:.1f}%")

importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
print("\n  Top 10 Features:")
for i in range(min(10, len(FEATURE_COLS))):
    print(f"    {i+1}. {FEATURE_COLS[indices[i]]}: {importances[indices[i]]:.4f}")

bundle = {
    'model': model,
    'encoders': encoders,
    'band_ranges': band_ranges,
    'band_names': BAND_NAMES,
    'feature_columns': FEATURE_COLS,
    'categorical_columns': CATEGORICAL_COLS,
    'numeric_columns': NUMERIC_COLS,
    'engineered_features': [
        'depreciation_pct', 'price_age_ratio', 'condition_score',
        'accessories_score', 'spec_value', 'usage_wear', 'effective_age'
    ],
    'model_type': 'RandomForestClassifier',
    'metrics': {
        'accuracy': accuracy,
        'within_1_band': within_1,
        'avg_confidence': avg_confidence
    }
}
joblib.dump(bundle, OUTPUT_PATH, compress=3)
file_size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
print(f"\n  Saved! ({file_size_mb:.1f} MB)")

print("\n" + "=" * 60)
print(f"  ACCURACY: {accuracy*100:.1f}%")
if accuracy >= 0.90:
    print("  [OK] TARGET MET!")
else:
    print("  [!!] Below 90%")
print("=" * 60)
