import base64
import pandas as pd
from flask import request, jsonify, send_file, render_template
from app import app, db
from models import ImportJob, FrappeConnection
from werkzeug.security import generate_password_hash
import requests
import os
import json
from werkzeug.utils import secure_filename
import logging

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def connect_frappe():
    data = request.json
    try:
        conn = FrappeConnection(
            url=data['url'],
            username=data['username']
        )
        conn.set_password(data['password'])
        db.session.add(conn)
        db.session.commit()
        return jsonify({"status": "success", "connection_id": conn.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/schema/<connection_id>', methods=['GET'])
def get_schema(connection_id):
    conn = FrappeConnection.query.get_or_404(connection_id)
    doctype = request.args.get('doctype')
    if not doctype:
        return jsonify({"status": "error", "message": "Doctype is required"}), 400

    try:
        # Use Frappe's built-in method to get doctype metadata
        response = requests.get(
            f"{conn.url}/api/method/frappe.desk.form.load.get_meta",
            params={"doctype": doctype},
            auth=(conn.username, conn.api_key)  # Use stored API key
        )
        meta_data = response.json()

        # Extract relevant field information
        fields = []
        if 'docs' in meta_data:
            for field in meta_data['docs'][0].get('fields', []):
                fields.append({
                    'fieldname': field.get('fieldname'),
                    'label': field.get('label'),
                    'fieldtype': field.get('fieldtype'),
                    'required': field.get('reqd', 0) == 1,
                })

        return jsonify({"fields": fields})
    except Exception as e:
        logging.error(f"Error getting schema: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/doctypes/<connection_id>', methods=['GET'])
def get_doctypes(connection_id):
    conn = FrappeConnection.query.get_or_404(connection_id)
    try:
        # Try to get doctypes using the desktop API endpoint
        response = requests.get(
            f"{conn.url}/api/resource/DocType?limit_page_length=10000",
            headers={
                'Authorization': f'token {conn.api_key}:{conn.api_secret}'
            } if conn.api_key and conn.api_secret else None,
        )
        if response.ok:
            data = response.json()
            if 'data' in data:
                return jsonify({"message": [x["name"] for x in data['data']]})

        logging.error(f"Failed to fetch doctypes. Response: {response.text}")
        return jsonify({"status": "error", "message": "Unable to fetch doctypes. Please check your credentials."}), 400

    except Exception as e:
        logging.error(f"Error getting doctypes: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        # Save the file
        file.save(filepath)

        # Read the file to get total rows
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            os.remove(filepath)
            return jsonify({"status": "error", "message": "Unsupported file format"}), 400

        # Create import job
        job = ImportJob(
            frappe_url=request.form.get('frappe_url'),
            doctype=request.form.get('doctype'),
            total_rows=len(df),
            file_path=filepath,
            batch_size=int(request.form.get('batch_size', 100))
        )
        db.session.add(job)
        db.session.commit()

        return jsonify({
            "status": "success",
            "job_id": job.id,
            "columns": df.columns.tolist(),
            "total_rows": len(df),
            "batch_size": job.batch_size
        })
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/import/<job_id>', methods=['POST'])
def import_data(job_id):
    job = ImportJob.query.get_or_404(job_id)
    mapping = request.json.get('mapping', {})

    try:
        # Read the file
        if job.file_path.endswith('.csv'):
            df = pd.read_csv(job.file_path)
        else:
            df = pd.read_excel(job.file_path)

        # Update job status
        job.status = 'processing'
        db.session.commit()

        # Process in batches
        total_batches = (len(df) + job.batch_size - 1) // job.batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * job.batch_size
            end_idx = min((batch_num + 1) * job.batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]

            # Map the data according to the provided mapping
            mapped_data = []
            for _, row in batch_df.iterrows():
                record = {frappe_field: row[excel_col] for excel_col, frappe_field in mapping.items()}
                mapped_data.append(record)

            # Here you would send the mapped_data to Frappe
            # For now, we'll just update the progress
            job.processed_rows = end_idx
            job.current_batch = batch_num + 1
            db.session.commit()

        # Update final status
        job.status = 'completed'
        db.session.commit()

        # Clean up the file
        if os.path.exists(job.file_path):
            os.remove(job.file_path)

        return jsonify({"status": "success", "message": "Import completed"})

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        db.session.commit()

        # Clean up on error
        if os.path.exists(job.file_path):
            os.remove(job.file_path)

        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = ImportJob.query.get_or_404(job_id)
    return jsonify({
        "status": job.status,
        "processed_rows": job.processed_rows,
        "total_rows": job.total_rows,
        "current_batch": job.current_batch,
        "total_batches": (job.total_rows + job.batch_size - 1) // job.batch_size if job.batch_size else 0,
        "error_message": job.error_message
    })