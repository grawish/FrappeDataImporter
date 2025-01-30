
from . import TemplateHandler

class CustomerTemplateHandler(TemplateHandler):
    def get_fields(self, selected_fields):
        # Use selected fields from frontend if provided
        # address_title, address_line1, address_line2, city, state, zipcode, country, phone, email, address_type
        selected_fields.append("customer_primary_address.address_title")
        selected_fields.append("customer_primary_address.address_line1")
        selected_fields.append("customer_primary_address.address_line2")
        selected_fields.append("customer_primary_address.city")
        selected_fields.append("customer_primary_address.state")
        selected_fields.append("customer_primary_address.zipcode")
        selected_fields.append("customer_primary_address.country")
        selected_fields.append("customer_primary_address.phone")
        selected_fields.append("customer_primary_address.email")
        selected_fields.append("customer_primary_address.address_type")
        selected_fields.append("customer_secondary_address.address_title")
        selected_fields.append("customer_secondary_address.address_line1")
        selected_fields.append("customer_secondary_address.address_line2")
        selected_fields.append("customer_secondary_address.city")
        selected_fields.append("customer_secondary_address.state")
        selected_fields.append("customer_secondary_address.zipcode")
        selected_fields.append("customer_secondary_address.country")
        selected_fields.append("customer_secondary_address.phone")
        selected_fields.append("customer_secondary_address.email")
        selected_fields.append("customer_secondary_address.address_type")

        return selected_fields

    def process_template(self, df):
        # Add any customer-specific processing here
        return df
