from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from app import db

health_bp = Blueprint("health", __name__)

# 1. Liveness Endpoint: Checks if the Flask application process is running
@health_bp.route('/live', methods=['GET'])
def live():
    # If the app can respond to this HTTP request, it is alive
    return jsonify({"status": "alive"}), 200

# 2. Readiness Endpoint: Checks if the app can successfully reach the database
@health_bp.route('/ready', methods=['GET'])
def ready():
    try:
        # Executes a lightweight query to test the database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "ready", "database": "connected"}), 200
    except Exception as e:
        # Logs the error internally using current_app and returns a 503 status
        current_app.logger.error(f"Database connection failed: {str(e)}")
        return jsonify({"status": "unready", "reason": "Database connection failed"}), 503