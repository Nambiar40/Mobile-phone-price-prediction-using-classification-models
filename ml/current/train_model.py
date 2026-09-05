import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier

def get_price_category(price):
    if price < 20000:
        return 'Entry-level (< 20K INR)'
    elif 20000 <= price < 35000:
        return 'Mid-range (20K - 35K INR)'
    elif 35000 <= price < 60000:
        return 'Upper Mid-range (35K - 60K INR)'
    elif 60000 <= price < 90000:
        return 'High-end (60K - 90K INR)'
    else:
        return 'Premium (> 90K INR)'

def main():
    print("Loading dataset...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'current price data', 'smartphone_dataset_1M.csv')
    
    # Read 100k rows randomly
    df = pd.read_csv(data_path, skiprows=lambda i: i > 0 and np.random.rand() > 0.1)
    
    print(f"Dataset sampled to {len(df)} rows.")
    
    # Create target classes
    df['price_category'] = df['price_inr'].apply(get_price_category)
    
    # Define features
    features = [
        'brand', 'os', 'launch_year', '5g_support', 'dual_sim', 
        'expandable_storage', 'water_resistance', 'wireless_charging', 
        'fingerprint_sensor', 'face_unlock', 
        'screen_to_body_ratio', 'build_material', 'colors_available', 
        'warranty_years', 'bluetooth_version', 'wifi_version', 'chipset', 
        'ram_gb', 'storage_gb', 'display_size_inch', 'display_type', 
        'refresh_rate_hz', 'battery_mah', 'fast_charging_w', 'camera_setup', 
        'weight_g', 'thickness_mm'
    ]
    
    # Intentionally EXCLUDING 'rear_camera_mp', 'front_camera_mp', 'model_name', 'cpu_score', 'gpu_score'
    
    X = df[features]
    y = df['price_category']
    
    # Label encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Define preprocessor
    categorical_features = ['brand', 'os', 'build_material', 'wifi_version', 'chipset', 'display_type', 'camera_setup']
    numeric_features = [f for f in features if f not in categorical_features]
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )
    
    # Create and train model pipeline
    print("Training XGBoost Classifier...")
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy on Test Set: {accuracy:.4f}")
    
    # Save model and encoder
    models_dir = os.path.join(base_dir, 'backend', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_out = os.path.join(models_dir, 'current_price_model.pkl')
    encoder_out = os.path.join(models_dir, 'current_price_label_encoder.pkl')
    
    joblib.dump(model, model_out)
    joblib.dump(le, encoder_out)
    
    # Also save to ml/current as backup
    joblib.dump(model, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'current_price_model.pkl'))
    joblib.dump(le, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'current_price_label_encoder.pkl'))
    
    print("Models saved successfully!")

if __name__ == '__main__':
    main()
