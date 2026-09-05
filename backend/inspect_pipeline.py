import joblib
import sklearn

if not hasattr(sklearn.compose._column_transformer, '_RemainderColsList'):
    class _RemainderColsList(list):
        pass
    sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

model = joblib.load('models/current_price_model.pkl')

print("Steps in pipeline:")
for name, step in model.steps:
    print(f"- {name}: {type(step)}")
    if name == 'preprocessor':
        print("\nPreprocessor Transformers:")
        for t_name, transformer, cols in step.transformers:
            if t_name != 'remainder':
                print(f"  * {t_name}: {cols}")
