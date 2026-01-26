import re
import joblib
from .safety_services import check_url_Safety

model = joblib.load("model/phishing_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

PHISHING_WORDS = [
    "verify", "suspend", "urgent", "security alert",
    "unusual activity", "login", "click", "confirm"
]

def detect_phishing(text, google_api_key):
    # ML prediction
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]

    # Rule-based boost
    rule_hit = sum(1 for w in PHISHING_WORDS if w in text.lower())

    # URL extraction
    urls = re.findall(r'https?://\S+', text)
    url_results = []

    for url in urls:
        status = check_url_Safety(url, google_api_key)
        url_results.append({"url": url, "status": status})

    if pred == 1 or rule_hit >= 2 or any(u["status"] == "Unsafe" for u in url_results):
        result = "Phishing / Spam"
    else:
        result = "Safe Message"

    return result, url_results
