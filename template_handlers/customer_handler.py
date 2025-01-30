from . import TemplateHandler
import requests
from models import FrappeConnection


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
        # this method will be used before importing the data
        # the dataframe must separate all the fields that are added into the template

        filtered_columns = [
            "customer_primary_address.address_title",
            "customer_primary_address.address_line1",
            "customer_primary_address.address_line2",
            "customer_primary_address.city", "customer_primary_address.state",
            "customer_primary_address.zipcode",
            "customer_primary_address.country",
            "customer_primary_address.phone", "customer_primary_address.email",
            "customer_primary_address.address_type",
            "customer_secondary_address.address_title",
            "customer_secondary_address.address_line1",
            "customer_secondary_address.address_line2",
            "customer_secondary_address.city",
            "customer_secondary_address.state",
            "customer_secondary_address.zipcode",
            "customer_secondary_address.country",
            "customer_secondary_address.phone",
            "customer_secondary_address.email",
            "customer_secondary_address.address_type"
        ]

        df_filtered = df[filtered_columns]

        # Now remove these columns from the original dataframe if needed
        df = df.drop(columns=filtered_columns)
        return (df, df_filtered)

    def import_filtered_data(self, df, filtered_df):
        # this method will be used after importing the filtered data if the data import is successful
        #get all the columns with primary address
        primary_Address_df = df.loc[:,
                                    df.columns.str.
                                    contains('customer_primary_address')]
        #get all the columns with secondary address
        secondary_Address_df = df.loc[:,
                                      df.columns.str.
                                      contains('customer_secondary_address')]
        # import primary address
        self.import_primary_address(conn, primary_Address_df)
        # import secondary address
        self.import_secondary_address(conn, secondary_Address_df)

    def import_primary_address(self, conn, df):
        conn = FrappeConnection.query.get_or_404(self.connection_id)
        # modify the df to remove customer_primary_address.<fieldname>
        df = df.rename(
            columns=lambda x: x.replace('customer_primary_address.', ''))
        try:
            import_primary_request = requests.post(
                conn.url + "/api/method/frappe.client.insert",
                json=df.to_dict(orient='records'),
                headers={
                    "Authorization": f'token {conn.api_key}:{conn.api_secret}'
                })
            if import_primary_request.ok:
                return import_primary_request.json()
        except Exception as e:
            print("Exception: " + str(e))
            raise e
    def import_secondary_address(self, conn, df):
        conn = FrappeConnection.query.get_or_404(self.connection_id)
        # modify the df to remove customer_secondary_address.<fieldname>
        df = df.rename(
            columns=lambda x: x.replace('customer_secondary_address.', ''))
        try:
            import_secondary_request = requests.post(
                conn.url + "/api/method/frappe.client.insert",
                json=df.to_dict(orient='records'),
                headers={
                    "Authorization": f'token {conn.api_key}:{conn.api_secret}'
                })
            if import_secondary_request.ok:
                return import_secondary_request.json()
        except Exception as e:
            print("Exception: " + str(e))
            raise e