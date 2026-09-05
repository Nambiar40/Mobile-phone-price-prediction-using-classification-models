import sys
import joblib
import pandas as pd
import sklearn

# Patch sklearn.compose._column_transformer if necessary
if not hasattr(sklearn.compose._column_transformer, '_RemainderColsList'):
    class _RemainderColsList(list):
        pass
    sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

try:
    model = joblib.load('../ml/current/current_price_model.pkl')
    print("Model type:", type(model))
    if hasattr(model, 'feature_names_in_'):
        print("Expected features:", list(model.feature_names_in_))
    else:
        print("Model has no feature_names_in_ attribute.")
        # if it's a pipeline, get features from the first step
        if hasattr(model, 'steps'):
            first_step = model.steps[0][1]
            if hasattr(first_step, 'feature_names_in_'):
                print("Expected features (from pipeline step):", list(first_step.feature_names_in_))
except Exception as e:
    print(f"Error loading model: {e}")
