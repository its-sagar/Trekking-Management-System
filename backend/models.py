from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin | staff | user
    full_name = db.Column(db.String(100), default='')
    phone = db.Column(db.String(20), default='')
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', back_populates='user', lazy=True)
    assigned_treks = db.relationship(
        'Trek', back_populates='staff', lazy=True, foreign_keys='Trek.assigned_staff_id'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat(),
        }


class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), default='')
    difficulty = db.Column(db.String(20), default='Moderate')  # Easy | Moderate | Hard
    duration_days = db.Column(db.Integer, default=1)
    available_slots = db.Column(db.Integer, default=0)
    total_slots = db.Column(db.Integer, default=0)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='Pending')  # Pending | Approved | Open | Closed | Completed
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', back_populates='trek', lazy=True)
    staff = db.relationship('User', back_populates='assigned_treks', foreign_keys=[assigned_staff_id])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'difficulty': self.difficulty,
            'duration_days': self.duration_days,
            'available_slots': self.available_slots,
            'total_slots': self.total_slots,
            'assigned_staff_id': self.assigned_staff_id,
            'assigned_staff_name': (self.staff.full_name or self.staff.username) if self.staff else None,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'booking_count': len([b for b in self.bookings if b.status == 'Booked']),
        }


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Booked')  # Booked | Cancelled | Completed
    payment_status = db.Column(db.String(20), default='Pending')  # Pending | Paid
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': (self.user.full_name or self.user.username) if self.user else None,
            'user_email': self.user.email if self.user else None,
            'trek_id': self.trek_id,
            'trek_name': self.trek.name if self.trek else None,
            'trek_location': self.trek.location if self.trek else None,
            'trek_difficulty': self.trek.difficulty if self.trek else None,
            'start_date': self.trek.start_date.isoformat() if self.trek and self.trek.start_date else None,
            'end_date': self.trek.end_date.isoformat() if self.trek and self.trek.end_date else None,
            'booking_date': self.booking_date.isoformat(),
            'status': self.status,
            'payment_status': self.payment_status,
            'notes': self.notes,
        }
