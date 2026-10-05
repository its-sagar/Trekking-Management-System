from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import Trek, Booking
from app import db, cache
from auth import role_required
from routes.admin_routes import invalidate_trek_cache

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/stats', methods=['GET'])
@role_required('staff')
def get_stats():
    user_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=user_id).all()
    total_participants = sum(
        Booking.query.filter_by(trek_id=t.id, status='Booked').count() for t in treks
    )
    return jsonify({
        'assigned_treks': len(treks),
        'total_participants': total_participants,
        'open_treks': sum(1 for t in treks if t.status == 'Open'),
        'completed_treks': sum(1 for t in treks if t.status == 'Completed'),
    }), 200


@staff_bp.route('/treks', methods=['GET'])
@role_required('staff')
def get_assigned_treks():
    user_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=user_id).all()
    result = []
    for trek in treks:
        t = trek.to_dict()
        t['participant_count'] = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        result.append(t)
    return jsonify(result), 200


@staff_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@role_required('staff')
def update_trek(trek_id):
    user_id = int(get_jwt_identity())
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=user_id).first_or_404()
    data = request.get_json()

    if 'available_slots' in data:
        trek.available_slots = max(0, int(data['available_slots']))
    if 'status' in data and data['status'] in ['Open', 'Closed', 'Completed']:
        trek.status = data['status']

    db.session.commit()
    invalidate_trek_cache(trek_id)
    return jsonify(trek.to_dict()), 200


@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@role_required('staff')
def get_participants(trek_id):
    user_id = int(get_jwt_identity())
    Trek.query.filter_by(id=trek_id, assigned_staff_id=user_id).first_or_404()
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200