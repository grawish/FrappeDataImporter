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
            pass




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