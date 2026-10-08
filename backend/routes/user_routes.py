import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import safe_join
from io import BytesIO
from models import User, Trek, Booking
from app import db, cache, make_dynamic_cache_key
from auth import role_required
from routes.admin_routes import invalidate_trek_cache


user_bp = Blueprint('user', __name__)


@user_bp.route('/treks', methods=['GET'])
@role_required('user')
@cache.cached(timeout=300, make_cache_key=make_dynamic_cache_key)
def get_open_treks():
    treks = Trek.query.filter_by(status='Open').order_by(Trek.start_date).all()
    return jsonify([t.to_dict() for t in treks]), 200


@user_bp.route('/treks/search', methods=['GET'])
@role_required('user')
def search_treks():
    q = request.args.get('q', '')
    difficulty = request.args.get('difficulty', '')
    location = request.args.get('location', '')
    max_duration = request.args.get('duration', '')

    query = Trek.query.filter(Trek.status.in_(['Open', 'Approved']))

    if q:
        query = query.filter(
            Trek.name.ilike(f'%{q}%')
            | Trek.location.ilike(f'%{q}%')
            | Trek.description.ilike(f'%{q}%')
        )
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))
    if max_duration:
        query = query.filter(Trek.duration_days <= int(max_duration))

    return jsonify([t.to_dict() for t in query.order_by(Trek.start_date).all()]), 200


@user_bp.route('/treks/<int:trek_id>', methods=['GET'])
@role_required('user')
@cache.cached(timeout=600, make_cache_key=make_dynamic_cache_key)
def get_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return jsonify(trek.to_dict()), 200


@user_bp.route('/treks/<int:trek_id>/book', methods=['POST'])
@role_required('user')
def book_trek(trek_id):
    user_id = int(get_jwt_identity())
    trek = Trek.query.get_or_404(trek_id)

    if trek.status != 'Open':
        return jsonify({'error': 'This trek is not open for bookings'}), 400
    if trek.available_slots <= 0:
        return jsonify({'error': 'No available slots for this trek'}), 400

    existing = Booking.query.filter_by(user_id=user_id, trek_id=trek_id, status='Booked').first()
    if existing:
        return jsonify({'error': 'You have already booked this trek'}), 409

    data = request.get_json() or {}
    booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        notes=data.get('notes', ''),
    )
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()

    invalidate_trek_cache(trek_id)

    return jsonify(booking.to_dict()), 201


@user_bp.route('/bookings', methods=['GET'])
@role_required('user')
def get_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@user_bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@role_required('user')
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first_or_404()

    if booking.status != 'Booked':
        return jsonify({'error': 'Only active bookings can be cancelled'}), 400

    booking.status = 'Cancelled'
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1

    db.session.commit()

    invalidate_trek_cache(booking.trek_id)

    return jsonify({'message': 'Booking cancelled successfully'}), 200


@user_bp.route('/profile', methods=['GET'])
@role_required('user')
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/profile', methods=['PUT'])
@role_required('user')
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()

    for field in ['full_name', 'phone']:
        if field in data:
            setattr(user, field, data[field])
    if data.get('password'):
        user.set_password(data['password'])

    db.session.commit()
    return jsonify(user.to_dict()), 200


@user_bp.route('/export-csv', methods=['POST'])
@role_required('user')
def export_csv():
    user_id = int(get_jwt_identity())
    try:
        from tasks import export_booking_csv
        # Send the task directly to the Redis background message queue
        task = export_booking_csv.delay(user_id)
        return jsonify({'message': 'CSV export started', 'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': f'Could not start export: {str(e)}. Is Celery running?'}), 503


@user_bp.route('/export-status/<task_id>', methods=['GET'])
@role_required('user')
def export_status(task_id):
    try:
        from tasks import export_booking_csv
        task = export_booking_csv.AsyncResult(task_id)
        state = task.state
        if state == 'SUCCESS':
            return jsonify({
                'status': 'success', 
                'task_id': task_id  # Pass back the task_id to allow downloading
            }), 200
        elif state == 'FAILURE':
            return jsonify({'status': 'failed', 'reason': str(task.result)}), 200
        else:
            return jsonify({'status': state.lower()}), 200
    except Exception as e:
        return jsonify({'status': 'unknown', 'error': str(e)}), 200


@user_bp.route('/download-csv/<task_id>', methods=['GET'])
@role_required('user')
def download_csv(task_id):
    try:
        from tasks import export_booking_csv
        task = export_booking_csv.AsyncResult(task_id)

        if task.state != 'SUCCESS':
            return jsonify({"error": "CSV file is not ready or export failed"}), 400

        # Pull the CSV text payload straight out of the shared Redis backend cache
        csv_content_string = task.result
        if not csv_content_string:
            return jsonify({"error": "CSV data is empty"}), 404

        # Format string text into standard transferable bytes
        csv_bytes = csv_content_string.encode('utf-8')

        current_app.logger.info(f"[CSV DOWNLOAD] Loaded {len(csv_bytes)} bytes from Redis for Task: {task_id}")

        # Clean up the data string out of Redis memory store to save storage space
        task.forget() 

        # Transmit the file securely stream-style down to the browser
        return send_file(
            BytesIO(csv_bytes),
            as_attachment=True,
            download_name=f"booking_export_{task_id}.csv",
            mimetype='text/csv'
        )

    except Exception as e:
        current_app.logger.error(f"[CSV DOWNLOAD ERROR] {str(e)}")
        return jsonify({"error": "Could not download CSV"}), 500