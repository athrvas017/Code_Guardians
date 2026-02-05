import os
import re
import joblib
from .safety_services import check_url_Safety

_here = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_here)
model = joblib.load(os.path.join(_backend_dir, "model", "phishing_model.pkl"))
vectorizer = joblib.load(os.path.join(_backend_dir, "model", "vectorizer.pkl"))

PHISHING_WORDS = [
    "verify", "suspend", "urgent", "security alert",
    "unusual activity", "login", "click", "confirm"
]

def detect_phishing(text, google_api_key):
    # ML prediction for text content
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]

    # Rule-based boost
    rule_hit = sum(1 for w in PHISHING_WORDS if w in text.lower())

    # URL extraction & Hybrid Check (ML + API)
    urls = re.findall(r'https?://\S+', text)
    url_results = []
    has_unsafe_url = False

    for url in urls:
        # returns "Unsafe" or "Safe"
        status = check_url_Safety(url, google_api_key)
        if status == "Unsafe":
            has_unsafe_url = True
        url_results.append({"url": url, "status": status})

    # Combined Verdict
    # If ML says phishing OR rule hits high OR any URL is unsafe
    if pred == 1 or rule_hit >= 2 or has_unsafe_url:
        result = "🚨 Phishing / Spam Detected"
    else:
        result = "✅ Safe Message"

    return result, url_results
