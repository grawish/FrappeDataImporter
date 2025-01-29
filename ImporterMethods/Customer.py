def validate(data):
    field_info = []
    for key in data.keys():
        # Extract field info from the key format: "fieldname [fieldtype] [options]"
        parts = key.split('[')
        fieldname = parts[0].strip()
        
        if len(parts) >= 2:
            fieldtype = parts[1].strip().rstrip(']')
            
            # Check if it's a Link field with options
            if fieldtype == 'Link' and len(parts) >= 3:
                options = parts[2].strip().rstrip(']')
                field_info.append({
                    'fieldname': fieldname,
                    'fieldtype': fieldtype,
                    'options': options
                })
            else:
                field_info.append({
                    'fieldname': fieldname,
                    'fieldtype': fieldtype
                })
    
    return field_info

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