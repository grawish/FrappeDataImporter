def validate(data):
  for key in data.keys():
    # extract fieldname, fieldtype and if link options
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