
from flask import request, jsonify
from app import db
from models import FrappeConnection
from . import api

@api.route('/connect', methods=['POST'])
def connect_frappe():
    data = request.json
    try:
        conn = FrappeConnection(
            url=data['url'],
            username=data['username']
        )
        conn.set_password(data['password'])

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

        db.session.add(conn)
        db.session.commit()
        return jsonify({"status": "success", "connection_id": conn.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
