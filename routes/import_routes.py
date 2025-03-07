import json
import os
import pandas as pd
from ImporterMethods.Customer import validate_all
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import db
from models import ImportJob
from . import api
import requests
from models import FrappeConnection
from ImporterMethods.Customer import get_field_mapping

UPLOAD_FOLDER = 'uploads'

@api.route('/upload', methods=['POST'])
def upload_file():

    connection_id = request.form.get('connection_id')
    if not connection_id:
        return jsonify({"status": "error", "message": "No connection ID provided"}), 400
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400

    conn = FrappeConnection.query.get_or_404(connection_id)
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            os.remove(filepath)
            return jsonify({"status": "error", "message": "Unsupported file format"}), 400

        validation_errors = validate_all(df.to_dict(orient='records'))
        if validation_errors:
            os.remove(filepath)
            raise ValueError(validation_errors)

        file_size = os.path.getsize(filepath)
        optimal_batch_size = 500 if file_size >= 20 * 1024 * 1024 else (
            250 if file_size >= 5 * 1024 * 1024 else (
                100 if file_size >= 1024 * 1024 else 50
            )
        )

        job = ImportJob(
            frappe_url=conn.url,
            doctype=request.form.get('doctype'),
            total_rows=len(df),
            file_path=filepath,
            batch_size=optimal_batch_size
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

@api.route('/import/<job_id>/<conn_id>', methods=['POST'])
def import_data(job_id, conn_id):
    job = ImportJob.query.get_or_404(job_id)
    mapping = request.json.get('mapping', {})

    try:
        if job.file_path.endswith('.csv'):
            df = pd.read_csv(job.file_path)
        else:
            df = pd.read_excel(job.file_path)

        job.status = 'processing'
        db.session.commit()

        total_batches = (len(df) + job.batch_size - 1) // job.batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * job.batch_size
            end_idx = min((batch_num + 1) * job.batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]

            mapped_data = []
            for _, row in batch_df.iterrows():
                record = {}
                child_tables = {}

                for excel_col in row.index:
                    fieldname, fieldtype, options = get_field_mapping(excel_col)
                    
                    if '.' in fieldname:
                        parts = fieldname.split('.')
                        if len(parts) == 3:
                            table_name, row_num, field_name = parts
                            row_num = int(row_num)

                            if table_name not in child_tables:
                                child_tables[table_name] = {}

                            if row_num not in child_tables[table_name]:
                                child_tables[table_name][row_num] = {}

                            if pd.notna(row[excel_col]) and str(row[excel_col]).strip():
                                child_tables[table_name][row_num][field_name] = row[excel_col]
                    else:
                        if pd.notna(row[excel_col]):
                            record[fieldname] = row[excel_col]

                for table_name, rows in child_tables.items():
                    valid_rows = [data for row_num, data in sorted(rows.items()) if data]
                    if valid_rows:
                        record[table_name] = valid_rows

                if record:
                    mapped_data.append(record)

            # Create records in Frappe using insert_many
            try:
                # Get connection details from frappe_url
                conn = FrappeConnection.query.get_or_404(conn_id)
                if not conn:
                    raise Exception("Connection not found for the given Frappe URL")

                docs = [{"doctype": job.doctype, **record} for record in mapped_data]

                print(json.dumps(docs))

                response = requests.post(
                    f"{conn.url}/api/method/frappe.client.insert_many",
                    json={"docs": docs},
                    headers={
                        'Authorization': f'token {conn.api_key}:{conn.api_secret}',
                        'Content-Type': 'application/json'
                    }
                )
                print("insert response ->>>> ",response.json())
                if not response.ok:
                    raise Exception(f"Failed to create records: {response.text}")
            except Exception as e:
                raise Exception(f"Error creating records: {str(e)}")

            job.processed_rows = end_idx
            job.current_batch = batch_num + 1
            db.session.commit()

        job.status = 'completed'
        db.session.commit()

        if os.path.exists(job.file_path):
            os.remove(job.file_path)

        return jsonify({"status": "success", "message": "Import completed"})

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        db.session.commit()

        if os.path.exists(job.file_path):
            os.remove(job.file_path)

        return jsonify({"status": "error", "message": str(e)}), 400