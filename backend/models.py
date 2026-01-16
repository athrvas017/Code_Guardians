from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class URLCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    result = db.Column(db.String(50))
    checked_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)
