import joblib
import sklearn

class _RemainderColsList(list): pass
if not hasattr(sklearn.compose._column_transformer, '_RemainderColsList'):
    sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

m = joblib.load('models/current_price_model.pkl')
ct = m.steps[0][1]
print("feature_names_in_:", m.feature_names_in_)
for name, trans, cols in ct.transformers_:
    print(name, cols)
