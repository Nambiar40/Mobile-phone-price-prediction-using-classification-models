import os
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import classification_report, confusion_matrix

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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, 'backend', 'models', 'current_price_model.pkl')
    encoder_path = os.path.join(base_dir, 'backend', 'models', 'current_price_label_encoder.pkl')
    data_path = os.path.join(base_dir, 'current price data', 'smartphone_dataset_1M.csv')

    print("Loading model...")
    model = joblib.load(model_path)
    le = joblib.load(encoder_path)

    print("Loading a test sample of 10,000 rows from dataset...")
    # Read ~10,000 rows to test accuracy per category
    df = pd.read_csv(data_path, skiprows=lambda i: i > 0 and np.random.rand() > 0.01)
    
    df['price_category'] = df['price_inr'].apply(get_price_category)
    
    expected_features = list(model.steps[0][1].feature_names_in_)
    X = df[expected_features]
    y_true = df['price_category']
    y_true_encoded = le.transform(y_true)

    print("\nPredicting on test data...")
    y_pred_encoded = model.predict(X)
    y_pred = le.inverse_transform(y_pred_encoded)

    print("\n=== CLASSIFICATION REPORT ===")
    print(classification_report(y_true, y_pred))

    print("\n=== RANDOM EXAMPLES FROM EACH CATEGORY ===")
    for category in le.classes_:
        # Find a row where the true category matches this
        subset = df[df['price_category'] == category]
        if not subset.empty:
            random_row = subset.sample(1).iloc[0]
            
            # Predict for this single row
            single_x = pd.DataFrame([random_row[expected_features].to_dict()])
            pred = le.inverse_transform(model.predict(single_x))[0]
            
            print(f"True: {category:<35} | Predicted: {pred:<35}")
            print(f"  -> Phone: {random_row['brand']} | RAM: {random_row['ram_gb']}GB | Chipset: {random_row['chipset']}")
            print(f"  -> Actual Price: {random_row['price_inr']} INR")
            print("-" * 80)

if __name__ == '__main__':
    main()
