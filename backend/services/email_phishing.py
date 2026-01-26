from flask import Blueprint, render_template, request
import re
import joblib
from safety_services import check_url_safety

email_phishing_bp = Blueprint("email_phishing", __name__)

GOOGLE_API_KEY = "PASTE_GOOGLE_API_KEY"

model = joblib.load("spam_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

@email_phishing_bp.route("/email-phishing", methods=["GET", "POST"])
def email_phishing():
    result = None
    url_results = []

    if request.method == "POST":
        text = request.form["email"]

        pred = model.predict(vectorizer.transform([text]))[0]
        result = "🚨 Spam / Phishing" if pred == 1 else "✅ Safe Message"

        if pred == 1:
            urls = re.findall(r'https?://\S+', text)
            for url in urls:
                status = check_url_safety(url, GOOGLE_API_KEY)
                url_results.append({"url": url, "status": status})

    return render_template(
        "email_phishing.html",
        result=result,
        url_results=url_results
    )
