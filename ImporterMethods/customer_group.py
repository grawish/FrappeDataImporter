
import requests
from models import FrappeConnection
from flask import request

def create_frappe_record(name):
    try:
        connection_id = request.form.get('connection_id')
        conn = FrappeConnection.query.get_or_404(connection_id)
        
        doc_data = {
            "doctype": "Customer Group",
            "customer_group_name": name,
            "parent_customer_group": "All Customer Groups"
        }
        
        response = requests.post(
            f"{conn.url}/api/method/frappe.client.insert",
            json={"doc": doc_data},
            headers={
                'Authorization': f'token {conn.api_key}:{conn.api_secret}',
                'Content-Type': 'application/json'
            }
        )
        
        if response.ok:
            return response.json()
        return None
        
    except Exception as e:
        print(f"Error creating Customer Group: {str(e)}")
        return None
