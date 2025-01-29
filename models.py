import json

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash
import requests


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
        # Get API key and secret from Frappe
        try:
            # First authenticate with username/password
            auth_response = requests.post(
                f"{self.url}/api/method/login",
                data={"usr": self.username, "pwd": password}
            )
            if auth_response.ok:
                # Get API key and secret
                key_response = requests.post(
                    f"{self.url}/api/method/frappe.core.doctype.user.user.generate_keys",
                    data={"user":auth_response.json()["full_name"]},
                    cookies=auth_response.cookies.get_dict()
                )
                user_response = requests.get(
                    f"{self.url}/api/resource/User/{auth_response.json()['full_name']}?fields=['*']",
                    cookies=auth_response.cookies.get_dict(),
                )
                if user_response.ok:
                    user_data = user_response.json().get('data', {})
                    self.api_key = user_data.get('api_key')
                    if key_response.ok:
                        data = key_response.json()
                        self.api_secret = data.get('message', {}).get('api_secret')
        except Exception as e:
            print("Exception: " + str(e))
            # If API key generation fails, fall back to password authentication
            self.api_key = None
            self.api_secret = None
