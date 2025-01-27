import pandas as pd
from flask import request, jsonify, send_file, render_template
from app import app, db
from models import ImportJob, FrappeConnection
from werkzeug.security import generate_password_hash
import requests
import io
import json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def connect_frappe():
    data = request.json
    try:
        conn = FrappeConnection(
            url=data['url'],
            username=data['username'],
            password_hash=generate_password_hash(data['password'])
        )
        db.session.add(conn)
        db.session.commit()
        return jsonify({"status": "success", "connection_id": conn.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/schema/<connection_id>', methods=['GET'])
def get_schema(connection_id):
    conn = FrappeConnection.query.get_or_404(connection_id)
    try:
        response = requests.get(
            f"{conn.url}/api/method/frappe.desk.form.get_meta",
            params={"doctype": request.args.get('doctype')},
            auth=(conn.username, conn.password_hash)
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    
    file = request.files['file']
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"status": "error", "message": "Invalid file format"}), 400

    try:
        df = pd.read_excel(file)
        job = ImportJob(
            frappe_url=request.form.get('frappe_url'),
            doctype=request.form.get('doctype'),
            total_rows=len(df)
        )
        db.session.add(job)
        db.session.commit()
        return jsonify({"status": "success", "job_id": job.id, "columns": df.columns.tolist()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/import/<job_id>', methods=['POST'])
def import_data(job_id):
    job = ImportJob.query.get_or_404(job_id)
    mapping = request.json.get('mapping', {})
    
    try:
        # Implementation of actual import logic would go here
        job.status = 'processing'
        db.session.commit()
        return jsonify({"status": "success", "message": "Import started"})
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        db.session.commit()
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = ImportJob.query.get_or_404(job_id)
    return jsonify({
        "status": job.status,
        "processed_rows": job.processed_rows,
        "total_rows": job.total_rows,
        "error_message": job.error_message
    })