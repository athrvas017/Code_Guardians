import os
from flask import Flask, render_template, send_from_directory
from models import db
from services.url_safety import url_safety_bp

# Get paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(backend_dir), 'frontend')

app = Flask(__name__, 
            static_folder=frontend_dir,
            static_url_path='/static',
            template_folder=os.path.join(backend_dir, 'templates'))

# Basic config
app.config["SECRET_KEY"] = "testkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB
db.init_app(app)

# Register this page
app.register_blueprint(url_safety_bp)

# Create DB tables
with app.app_context():
    db.create_all()

# Home route - serve index.html as landing page
@app.route("/")
def home():
    return send_from_directory(os.path.join(frontend_dir, 'pages'), 'index.html')

# Password toolkit route
@app.route("/password")
def password():
    return send_from_directory(os.path.join(frontend_dir, 'pages'), 'pass.html')

if __name__ == "__main__":
    app.run(debug=True)
