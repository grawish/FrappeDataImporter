import requests
from models import FrappeConnection

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

def validate(doctype, data):
    for key in data.keys():
        fieldname, fieldtype, options = get_field_mapping(key)
        fieldvalue = data[key]
        
        if fieldtype == 'Select' and options:
            if fieldvalue not in options.split(', '):
                raise ValueError(f"Invalid value '{fieldvalue}' for field '{fieldname}'. Valid options are: {options}.")
        elif fieldtype == 'Link' and options:
            # Get connection details from the database
            conn = FrappeConnection.query.first()  # You'll need to pass the correct connection
            if not fieldvalue:  # Skip validation for empty values
                continue
                
            try:
                response = requests.get(
                    f"{conn.url}/api/method/frappe.client.validate_link",
                    params={
                        "doctype": options,
                        "docname": fieldvalue,
                        "fields": ["name"]
                    },
                    headers={'Authorization': f'token {conn.api_key}:{conn.api_secret}'} if conn.api_key and conn.api_secret else None
                )
                
                if not response.ok:
                    raise ValueError(f"Invalid value '{fieldvalue}' for field '{fieldname}'. Document not found in {options}.")
                    
            except Exception as e:
                raise ValueError(f"Error validating link for {fieldname}: {str(e)}")




data = {
    "customer_name [Data]": "Hybrowlabs",
    "customer_type [Select]": "Company",
    "customer_group [Link [Customer Group]]": "important customer",
    "territory [Link [Territory]]": "India",
    "default_currency [Link [Currency]]": "INR",
    "default_price_list [Link [Price List]]": None,  # Empty cell
    "tax_id [Data]": None,  # Empty cell
    "payment_terms [Link [Payment Terms Template]]": None  # Empty cell
}
validate(data)