import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the backend directory path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from flask import Blueprint, render_template, request
from models import db, URLCheck
from .safety_services import check_url_safety

# Set template folder to backend/templates
template_dir = os.path.join(backend_dir, 'templates')
url_safety_bp = Blueprint("url_safety", __name__, template_folder=template_dir)

# 🔐 Load API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@url_safety_bp.route("/url-safety", methods=["GET", "POST"])
def url_safety():
    result = None

    # user_id comes from existing login system
    user_id = 1  

    if request.method == "POST":
        url = request.form["url"]
        result = check_url_safety(url, GOOGLE_API_KEY)

        record = URLCheck(
            url=url,
            result=result,
            user_id=user_id
        )
        db.session.add(record)
        db.session.commit()

    history = URLCheck.query.filter_by(user_id=user_id).all()
    return render_template("url_safety.html", result=result, history=history)
