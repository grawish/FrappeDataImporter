
import logging
import requests
from flask import request, jsonify, send_file
import pandas as pd
import os
from app import db
from models import FrappeConnection
from . import api

UPLOAD_FOLDER = 'uploads'

@api.route('/schema/<connection_id>', methods=['GET'])
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

@api.route('/template/<connection_id>', methods=['POST'])
def get_template(connection_id):
    conn = FrappeConnection.query.get_or_404(connection_id)
    data = request.json
    doctype = data.get('doctype')
    selected_fields = data.get('fields', [])

    if not doctype:
        return jsonify({"status": "error", "message": "Doctype is required"}), 400

    try:
        response = requests.get(
            f"{conn.url}/api/method/frappe.desk.form.load.getdoctype",
            params={"doctype": doctype, "with_parent": 1},
            headers={'Authorization': f'token {conn.api_key}:{conn.api_secret}'} if conn.api_key and conn.api_secret else None
        )

        if not response.ok:
            return jsonify({"status": "error", "message": "Failed to fetch schema"}), 400

        schema_data = response.json()
        all_fields = {}
        main_fields = schema_data['docs'][0]['fields']

        for field in main_fields:
            if field['fieldtype'] == 'Table':
                child_doc = next((d for d in schema_data['docs'] if d['name'] == field['options']), None)
                if child_doc and isinstance(child_doc, dict) and 'fields' in child_doc:
                    for child_field in child_doc['fields']:
                        if isinstance(child_field, dict) and 'fieldname' in child_field:
                            qualified_name = f"{field['fieldname']}.{child_field['fieldname']}"
                            field_type = child_field.get('fieldtype', '')
                            if field_type.endswith('Link'):
                                field_type = f"{field_type} [{child_field.get('options', '')}]"
                            all_fields[qualified_name] = field_type
            elif isinstance(field, dict) and 'fieldname' in field:
                field_type = field.get('fieldtype', '')
                if field_type.endswith('Link'):
                    field_type = f"{field_type} [{field.get('options', '')}]"
                all_fields[field['fieldname']] = field_type

        ordered_fields = []
        for field_name in selected_fields:
            if field_name in all_fields:
                ordered_fields.append((field_name, all_fields[field_name]))

        columns = []
        for field_name, field_type in ordered_fields:
            if isinstance(field_type, str):
                if field_type.endswith('Link'):
                    parts = field_type.split(' [')
                    base_type = parts[0]
                    options = parts[1][:-1] if len(parts) > 1 else ''
                    columns.append(f"{field_name} [{base_type}] [{options}]")
                else:
                    columns.append(f"{field_name} [{field_type}]")

        df = pd.DataFrame(columns=columns)
        excel_file = os.path.join(UPLOAD_FOLDER, f'{doctype}_template.xlsx')
        writer = pd.ExcelWriter(excel_file, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Template')
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

@api.route('/doctypes/<connection_id>', methods=['GET'])
def get_doctypes(connection_id):
    conn = FrappeConnection.query.get_or_404(connection_id)
    try:
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
        return jsonify({"status": "error", "message": "Unable to fetch doctypes"}), 400

    except Exception as e:
        logging.error(f"Error getting doctypes: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400
