from flask import Blueprint, request, jsonify 
from models import User, Trek, Booking
from app import db, cache
from auth import role_required
from datetime import datetime
from sqlalchemy import func


admin_bp = Blueprint('admin', __name__)


def invalidate_trek_cache(trek_id=None):
    try:
        cache.clear()
    except Exception:
        pass


# ── Stats ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    return jsonify({
        'total_treks': Trek.query.count(),
        'total_users': User.query.filter_by(role='user').count(),
        'total_staff': User.query.filter_by(role='staff').count(),
        'total_bookings': Booking.query.count(),
        'open_treks': Trek.query.filter_by(status='Open').count(),
        'active_bookings': Booking.query.filter_by(status='Booked').count(),
    }), 200

# ── Treks ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/treks', methods=['GET'])
@role_required('admin')
def get_treks():
    q = request.args.get('q', '')
    difficulty = request.args.get('difficulty', '')
    status = request.args.get('status', '')

    query = Trek.query
    if q:
        query = query.filter(
            Trek.name.ilike(f'%{q}%') | Trek.location.ilike(f'%{q}%')
        )
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if status:
        query = query.filter_by(status=status)

    treks = query.order_by(Trek.created_at.desc()).all()
    return jsonify([t.to_dict() for t in treks]), 200


@admin_bp.route('/treks', methods=['POST'])
@role_required('admin')
def create_trek():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Trek name is required'}), 400

    total = data.get('total_slots', 20)
    trek = Trek(
        name=data.get('name'),
        location=data.get('location', ''),
        difficulty=data.get('difficulty', 'Moderate'),
        duration_days=int(data.get('duration_days', 1)),
        total_slots=int(total),
        available_slots=int(total),
        status='Pending',
        description=data.get('description', ''),
        price=int(data.get('price', 0)),
        image_url=data.get('image_url', ''),
    )
    if data.get('start_date'):
        trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if data.get('end_date'):
        trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    db.session.add(trek)
    db.session.commit()
    invalidate_trek_cache()
    return jsonify(trek.to_dict()), 201


@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@role_required('admin')
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()

    for field in ['name', 'location', 'difficulty', 'duration_days',
                  'total_slots', 'available_slots', 'status', 'description', 'price', 'image_url']:
        if field in data:
            setattr(trek, field, data[field])

    if 'start_date' in data and data['start_date']:
        trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data and data['end_date']:
        trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    db.session.commit()
    invalidate_trek_cache(trek_id)
    return jsonify(trek.to_dict()), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@role_required('admin')
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    invalidate_trek_cache(trek_id)
    return jsonify({'message': 'Trek deleted successfully'}), 200


@admin_bp.route('/treks/<int:trek_id>/assign-staff', methods=['POST'])
@role_required('admin')
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()
    staff_id = data.get('staff_id')

    if staff_id:
        staff = User.query.filter_by(id=staff_id, role='staff').first()
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        trek.assigned_staff_id = staff_id
    else:
        trek.assigned_staff_id = None

    db.session.commit()
    invalidate_trek_cache(trek_id)
    return jsonify(trek.to_dict()), 200


# ── Staff ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/staff', methods=['GET'])
@role_required('admin')
def get_staff():
    q = request.args.get('q', '')
    query = User.query.filter_by(role='staff')
    if q:
        query = query.filter(
            User.full_name.ilike(f'%{q}%') | User.email.ilike(f'%{q}%') | User.username.ilike(f'%{q}%')
        )
    return jsonify([s.to_dict() for s in query.all()]), 200


@admin_bp.route('/staff', methods=['POST'])
@role_required('admin')
def create_staff():
    data = request.get_json()
    for field in ['username', 'email', 'password', 'full_name']:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already in use'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already in use'}), 409

    staff = User(
        username=data['username'],
        email=data['email'],
        role='staff',
        full_name=data['full_name'],
        phone=data.get('phone', ''),
    )
    staff.set_password(data['password'])
    db.session.add(staff)
    db.session.commit()
    return jsonify(staff.to_dict()), 201


@admin_bp.route('/staff/<int:staff_id>', methods=['PUT'])
@role_required('admin')
def update_staff(staff_id):
    staff = User.query.filter_by(id=staff_id, role='staff').first_or_404()
    data = request.get_json()
    for field in ['full_name', 'phone', 'is_active', 'is_blacklisted']:
        if field in data:
            setattr(staff, field, data[field])
    db.session.commit()
    return jsonify(staff.to_dict()), 200


# ── Users ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    q = request.args.get('q', '')
    query = User.query.filter_by(role='user')
    if q:
        query = query.filter(
            User.username.ilike(f'%{q}%') | User.email.ilike(f'%{q}%') | User.full_name.ilike(f'%{q}%')
        )
    return jsonify([u.to_dict() for u in query.all()]), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@role_required('admin')
def update_user_status(user_id):
    user = User.query.filter_by(id=user_id, role='user').first_or_404()
    data = request.get_json()
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'is_blacklisted' in data:
        user.is_blacklisted = data['is_blacklisted']
    db.session.commit()
    return jsonify(user.to_dict()), 200


# ── Bookings ───────────────────────────────────────────────────────────────────

@admin_bp.route('/bookings', methods=['GET'])
@role_required('admin')
def get_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


# ── Analytics & Reports ────────────────────────────────────────────────────────

@admin_bp.route('/chart/bookings', methods=['GET'])
@role_required('admin')
def chart_bookings():
    results = (
        db.session.query(Trek.name, func.count(Booking.id).label('count'))
        .join(Booking, Trek.id == Booking.trek_id)
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc())
        .limit(7)
        .all()
    )
    return jsonify({
        'labels': [r[0] for r in results],
        'data': [r[1] for r in results],
    }), 200


@admin_bp.route('/reports/monthly', methods=['GET'])
@role_required('admin')
def monthly_report():
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)

    total_treks = Trek.query.filter(Trek.created_at >= start).count()
    total_bookings = Booking.query.filter(Booking.created_at >= start).count()
    total_participants = (
        db.session.query(func.count(func.distinct(Booking.user_id)))
        .filter(Booking.created_at >= start)
        .scalar()
    )

    popular = (
        db.session.query(Trek.name, func.count(Booking.id).label('count'))
        .join(Booking, Trek.id == Booking.trek_id)
        .filter(Booking.created_at >= start)
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
        .all()
    )

    return jsonify({
        'month': now.strftime('%B %Y'),
        'total_treks': total_treks,
        'total_bookings': total_bookings,
        'total_participants': total_participants or 0,
        'popular_treks': [{'name': p[0], 'bookings': p[1]} for p in popular],
    }), 200