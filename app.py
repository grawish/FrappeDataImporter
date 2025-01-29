
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
migrate = Migrate(app, db)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "https://localhost:5000", "*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "frappe-importer-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///frappe_importer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

from routes import api
app.register_blueprint(api, url_prefix='/api')

with app.app_context():
    import models
    db.create_all()
