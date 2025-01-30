import requests
import math
import json
from models import FrappeConnection
from flask import request


def get_field_mapping(key):
    # Extract field info from the key format: "fieldname [fieldtype] [options]"
    parts = key.split('[')
    fieldname = parts[0].strip()

    if len(parts) >= 2:
        fieldtype = parts[1].strip().rstrip(']')

        # Check if it's a Link field with options
        if fieldtype == 'Link' and len(parts) >= 3:
            options = parts[2].strip().rstrip(']')
            return fieldname, fieldtype, options
        else:
            return fieldname, fieldtype, None
    else:
        return fieldname, None, None


def validate_all(data_list):
    all_errors = ""
    for idx, data in enumerate(data_list):
        row_errors = validate_and_create(data)
        if row_errors and len(row_errors) > 0:
            all_errors += f"<b>Row {idx + 1}:</b><br>{row_errors}<br>"
    return all_errors


def validate_and_create(data):
    errors = ""
    for key in data.keys():
        fieldname, fieldtype, options = get_field_mapping(key)
        fieldvalue = data[key]

        if type(fieldvalue) is float and math.isnan(fieldvalue):
            continue
        if fieldtype == 'Select' and options:
            if fieldvalue not in options.split(', '):
                errors+=f"Invalid value '{fieldvalue}' for field '{fieldname}'. Valid options are: {options}. <br>"
                
        elif fieldtype == 'Link' and options:
            connection_id = request.form.get('connection_id')
            conn = FrappeConnection.query.get_or_404(connection_id)
            if not fieldvalue:  # Skip validation for empty values
                continue

            try:
                response = requests.get(
                    f"{conn.url}/api/method/frappe.client.validate_link?doctype={options}&docname={fieldvalue}&fields=[\"name\"]",
                    headers={
                        'Authorization':
                        f'token {conn.api_key}:{conn.api_secret}'
                    } if conn.api_key and conn.api_secret else None)

                if response.ok:
                    if not response.json().get('message', {}).get("name"):
                        create_missing = request.form.get('create_missing_records', '').lower() == 'true'
                        if create_missing:
                            from ImporterMethods.customer_group import create_frappe_record    
                            try:
                                create_frappe_record(fieldvalue)
                            except Exception as e:
                                errors+=(f"Error creating Customer Group: {str(e)}<br>")
                        else:
                            errors+=(f"Invalid value '{fieldvalue}' for field '{fieldname}'.<br>")
                        

            except Exception as e:
                errors+=f"Error validating link for {fieldname}:{str(e)} <br>"
    return errors
