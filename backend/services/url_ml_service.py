import os
import joblib
import pandas as pd
import validators
from .url_features import build_feature_matrix

# Load trained model
# Assuming this file is in backend/services/, model is in backend/model/
_here = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_here)
_model_dir = os.path.join(_backend_dir, "model")

# Lazy loading to avoid circular import issues or load on startup if preferred
model = None
vectorizer = None

def load_model():
    global model, vectorizer
    if model is None:
        try:
            model = joblib.load(os.path.join(_model_dir, "url_model.pkl"))
            vectorizer = joblib.load(os.path.join(_model_dir, "url_vectorizer.pkl"))
        except FileNotFoundError:
            print("⚠️ URL ML Model not found in backend/model/")

def check_url_ml(url):
    load_model()
    if not model or not vectorizer:
        return "⚠️ Model Error"

    if not validators.url(url):
        return "❌ Invalid URL"

    try:
        url_vec = build_feature_matrix(pd.Series([url]), vectorizer)
        prediction = model.predict(url_vec)[0]

        if prediction == 1:
            return "🚨 Phishing / Unsafe URL"
        else:
            return "✅ Safe URL"
    except Exception as e:
        print(f"Error in check_url_ml: {e}")
        return "⚠️ Analysis Error"
