
from . import TemplateHandler

class CustomerTemplateHandler(TemplateHandler):
    def get_fields(self):
        return [
            "customer_name [Data]",
            "customer_type [Select] [Company, Individual]",
            "customer_group [Link] [Customer Group]",
            "territory [Link] [Territory]",
            "address.address_line1 [Data]",
            "address.city [Data]",
            "address.state [Data]",
            "address.country [Data]",
            "address.pincode [Data]",
            "address.address_type [Select] [Billing, Shipping]",
            "address.is_primary_address [Check]",
            "tax_id [Data]",
            "gstin [Data]"
        ]

    def process_template(self, df):
        # Add any customer-specific processing here
        return df
