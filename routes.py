import pandas as pd
from flask import request, jsonify, send_file, render_template
from app import app, db
from models import ImportJob, FrappeConnection
from werkzeug.security import generate_password_hash
import requests
import os
import json
from werkzeug.utils import secure_filename

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