from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class ImportJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frappe_url = db.Column(db.String(256), nullable=False)
    doctype = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(32), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_rows = db.Column(db.Integer, default=0)
    processed_rows = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    batch_size = db.Column(db.Integer, default=100)
    current_batch = db.Column(db.Integer, default=0)
    file_path = db.Column(db.String(512))  # Store uploaded file path

class FrappeConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    api_key = db.Column(db.String(256), nullable=True)  # For API authentication
    api_secret = db.Column(db.String(256), nullable=True)  # For API authentication
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        # Store API credentials for Frappe server calls
        self.api_key = password  # Temporarily store password for API calls