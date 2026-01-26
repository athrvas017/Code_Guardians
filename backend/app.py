import os
from flask import Flask, render_template, request, send_from_directory
from services.url_safety import url_safety_bp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(backend_dir), 'frontend')

app = Flask(__name__, 
            static_folder=frontend_dir,
            static_url_path='/static',
            template_folder=os.path.join(backend_dir, 'templates'))

# Basic config
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "testkey")

# Google API Key for Safe Browsing
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Register this page
app.register_blueprint(url_safety_bp)

# Home route - serve index.html as landing page
@app.route("/")
def home():
    return send_from_directory(os.path.join(frontend_dir, 'pages'), 'index.html')

# Password toolkit route
@app.route("/password")
def password():
    return send_from_directory(os.path.join(frontend_dir, 'pages'), 'pass.html')

# Phishing detector route
@app.route("/phishing", methods=["GET", "POST"])
def phishing():
    result = None
    url_results = []

    if request.method == "POST":
        try:
            from services.phishing_service import detect_phishing
            text = request.form.get("message", "")
            if text and GOOGLE_API_KEY:
                result, url_results = detect_phishing(text, GOOGLE_API_KEY)
            elif not GOOGLE_API_KEY:
                result = "API key not configured"
        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template('phishing.html', result=result, url_results=url_results)

# Cyber Awareness route
@app.route("/awareness")
def awareness():
    return send_from_directory(os.path.join(frontend_dir, 'pages'), 'awareness.html')

# AI Image Detection Route
@app.route("/ai-detection", methods=["GET", "POST"])
def ai_detection():
    if request.method == "GET":
        return send_from_directory(os.path.join(frontend_dir, 'pages'), 'ai-detection.html')

    # POST - Image Analysis
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400
    
    file = request.files['image']
    if file.filename == '':
        return {"error": "No selected file"}, 400

    if file:
        # Save temp file
        uploads_dir = os.path.join(backend_dir, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filepath = os.path.join(uploads_dir, file.filename)
        file.save(filepath)

        try:
            from services.ai_image_detection import detect_image
            result = detect_image(filepath)
            
            # Clean up
            if os.path.exists(filepath):
                os.remove(filepath)
                
            return result
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)
