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
        response = requests.get(
            f"{conn.url}/api/method/frappe.desk.form.load.getdoctype",
            params={"doctype": doctype, "with_parent": 1},
            headers={'Authorization': f'token {conn.api_key}:{conn.api_secret}'} if conn.api_key and conn.api_secret else None
        )
        if response.ok:
            schema_data = response.json()
            return jsonify(schema_data)
        
        logging.error(f"Failed to fetch schema. Response: {response.text}")
        return jsonify({"status": "error", "message": "Unable to fetch schema"}), 400
    except Exception as e:
        logging.error(f"Error getting schema: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/template/<connection_id>', methods=['POST'])
def get_template(connection_id):
    conn = FrappeConnection.query.get_or_404(connection_id)
    data = request.json
    doctype = data.get('doctype')
    selected_fields = data.get('fields', [])
    
    if not doctype:
        return jsonify({"status": "error", "message": "Doctype is required"}), 400

    try:
        # Get doctype schema
        response = requests.get(
            f"{conn.url}/api/method/frappe.desk.form.load.getdoctype",
            params={"doctype": doctype, "with_parent": 1},
            headers={'Authorization': f'token {conn.api_key}:{conn.api_secret}'} if conn.api_key and conn.api_secret else None
        )
        
        if not response.ok:
            return jsonify({"status": "error", "message": "Failed to fetch schema"}), 400
            
        schema_data = response.json()
        
        # Get main fields
        all_fields = {}
        main_fields = schema_data['docs'][0]['fields']
        
        # Process main fields
        for field in main_fields:
            if field['fieldtype'] == 'Table':
                # Find child table schema
                child_doc = next((d for d in schema_data['docs'] if d['name'] == field['options']), None)
                if child_doc and 'fields' in child_doc:
                    # Add child fields with qualified names
                    for child_field in child_doc['fields']:
                        if 'fieldname' in child_field:
                            qualified_name = f"{field['fieldname']}.{child_field['fieldname']}"
                            all_fields[qualified_name] = child_field['fieldtype']
            elif 'fieldname' in field:
                all_fields[field['fieldname']] = field['fieldtype']

        # Create column headers with field types
        columns = []
        for field in selected_fields:
            fieldtype = all_fields.get(field, '')
            if fieldtype:  # Only add fields that we found types for
                columns.append(f"{field} [{fieldtype}]")
        
        # Process columns to handle child tables
        final_columns = []
        child_table_info = {}
        max_rows = 5  # Number of rows for child tables
        
        for field in schema_data['docs'][0]['fields']:
            if field['fieldtype'] == 'Table':
                child_doc = next((d for d in schema_data['docs'] if d['name'] == field['options']), None)
                if child_doc and 'fields' in child_doc:
                    child_fields = [f for f in child_doc['fields'] 
                                  if not f['hidden'] and not f['read_only'] and
                                  not f['fieldtype'] in ['Section Break', 'Column Break', 'Tab Break', 'Table', 'Read Only'] and
                                  not f['fieldtype'].endswith('Link')]
                    
                    child_table_info[field['fieldname']] = {
                        'fields': child_fields,
                        'count': max_rows
                    }
                    
                    # Add numbered columns for each child field
                    for i in range(1, max_rows + 1):
                        for child_field in child_fields:
                            col_name = f"{field['fieldname']}.{i}.{child_field['fieldname']} [{child_field['fieldtype']}]"
                            final_columns.append(col_name)
            else:
                if field['fieldname'] in selected_fields:
                    final_columns.append(f"{field['fieldname']} [{field['fieldtype']}]")

        # Create Excel template with formatted headers
        df = pd.DataFrame(columns=final_columns)
        
        # Save to temporary file with instructions
        excel_file = os.path.join(UPLOAD_FOLDER, f'{doctype}_template.xlsx')
        writer = pd.ExcelWriter(excel_file, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Template')
        
        # Add instructions sheet
        instructions = pd.DataFrame({
            'Instructions': [
                'For child tables:',
                f'- Each child table has {max_rows} sets of columns',
                '- Column format: tablename.row_number.fieldname',
                '- Example: items.1.item_name, items.2.item_name',
                '- Leave cells empty if not needed'
            ]
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
        writer.close()
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=f'{doctype}_template.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logging.error(f"Error generating template: {str(e)}")
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

        # Calculate optimal batch size based on file size
        file_size = os.path.getsize(filepath)
        if file_size < 1024 * 1024:  # < 1MB
            optimal_batch_size = 50
        elif file_size < 5 * 1024 * 1024:  # < 5MB
            optimal_batch_size = 100
        elif file_size < 20 * 1024 * 1024:  # < 20MB
            optimal_batch_size = 250
        else:
            optimal_batch_size = 500

        # Create import job
        job = ImportJob(
            frappe_url=request.form.get('frappe_url'),
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
                record = {}
                child_tables = {}
                
                # Process each excel column
                for excel_col, frappe_field in mapping.items():
                    # Check if this is a child table field
                    if '.' in excel_col:
                        parts = excel_col.split('.')
                        if len(parts) == 3:  # format: table_name.row_number.field_name
                            table_name, row_num, field_name = parts
                            row_num = int(row_num)
                            
                            # Initialize child table if needed
                            if table_name not in child_tables:
                                child_tables[table_name] = {}
                            
                            # Initialize row if needed
                            if row_num not in child_tables[table_name]:
                                child_tables[table_name][row_num] = {}
                            
                            # Add value if not empty
                            if pd.notna(row[excel_col]) and str(row[excel_col]).strip():
                                child_tables[table_name][row_num][field_name] = row[excel_col]
                    else:
                        # Handle main document fields
                        if pd.notna(row[excel_col]):
                            record[frappe_field] = row[excel_col]
                
                # Convert child tables to lists and add to record
                for table_name, rows in child_tables.items():
                    valid_rows = [data for row_num, data in sorted(rows.items()) if data]
                    if valid_rows:
                        record[table_name] = valid_rows
                
                if record:  # Only add non-empty records
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