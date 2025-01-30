
from flask import request, jsonify
from app import db
from models import FrappeConnection
from . import api

@api.route('/connect', methods=['POST'])
def connect_frappe():
    breakpoint()
    data = request.json
    try:
        # Check if connection already exists
        existing_conn = FrappeConnection.query.filter_by(
            url=data['url'],
            username=data['username']
        ).first()
        
        if existing_conn:
            existing_conn.set_password(data['password'])
            db.session.commit()
            return jsonify({"status": "success", "connection_id": existing_conn.id})
            
        # Create new connection if doesn't exist
        conn = FrappeConnection(
            url=data['url'],
            username=data['username']
        )
        conn.set_password(data['password'])
        db.session.add(conn)
        db.session.commit()
        return jsonify({"status": "success", "connection_id": conn.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@api.route('/connections', methods=['GET'])
def get_connections():
    try:
        connections = FrappeConnection.query.all()
        return jsonify({
            "status": "success",
            "connections": [
                {
                    "id": conn.id,
                    "url": conn.url,
                    "username": conn.username,
                    "created_at": conn.created_at.isoformat()
                } for conn in connections
            ]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@api.route('/connections/<int:connection_id>', methods=['DELETE'])
def delete_connection(connection_id):
    try:
        connection = FrappeConnection.query.get_or_404(connection_id)
        db.session.delete(connection)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
