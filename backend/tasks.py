"""
Celery tasks for TMA:
  - send_daily_reminders  (scheduled daily @ 08:00 UTC)
  - generate_monthly_report (scheduled 1st of month @ 07:00 UTC)
  - export_booking_csv    (user-triggered async)
"""
import os
import csv
import io
from datetime import datetime, date, timedelta
from flask_mailman import EmailMessage
from celery.schedules import crontab
from app import create_app, make_celery

flask_app = create_app()
celery_app = make_celery(flask_app)

celery_app.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=7, minute=0),
    },
}
celery_app.conf.timezone = 'UTC'


# ── Task: Daily Reminders ──────────────────────────────────────────────────────

@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    from models import Booking, Trek

    today = date.today()
    upcoming = Trek.query.filter(
        Trek.start_date >= today,
        Trek.start_date <= today + timedelta(days=7),
        Trek.status == 'Open',
    ).all()

    count = 0
    emails_sent = 0
    for trek in upcoming:
        bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
        for b in bookings:
            days_left = (trek.start_date - today).days
            user = b.user

            # Construct HTML email body content safely
            email_body = f"""
            <h3>Hello {user.username},</h3>
            <p>This is a quick reminder that your adventure trip <strong>"{trek.name}"</strong> 
            starts in <strong>{days_left} days</strong> on {trek.start_date.strftime('%B %d, %Y')}!</p>
            <p>Make sure to finalize your packing checklist and gather your gear items.</p>
            <br>
            <p>Best regards,<br>The Trekking Management Team</p>
            """
            
            try:
                msg = EmailMessage(
                    subject=f"⚠️ Adventure Reminder: {trek.name} in {days_left} Days!",
                    body=email_body,
                    to=[user.email]
                )
                msg.content_subtype = "html"  # Render body text layout as pure HTML
                msg.send()
                emails_sent += 1
                
            except Exception as e:
                # Capture failures cleanly without breaking the main loop for other users
                print(f"❌ Failed to dispatch email to {user.email}. Error: {str(e)}")

            print(
                f'[REMINDER] → {b.user.email} | '
                f'Trek: "{trek.name}" starts in {days_left} day(s) on {trek.start_date}'
            )
            count += 1

    return f'Sent {count} reminder(s) for {len(upcoming)} upcoming trek(s).'


# ── Task: Monthly Activity Report ─────────────────────────────────────────────

@celery_app.task(name='tasks.generate_monthly_report')
def generate_monthly_report():
    from models import Trek, Booking, User
    from app import db
    from sqlalchemy import func

    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)

    total_treks = Trek.query.filter(Trek.created_at >= start).count()
    total_bookings = Booking.query.filter(Booking.created_at >= start).count()
    participants = (
        db.session.query(func.count(func.distinct(Booking.user_id)))
        .filter(Booking.created_at >= start)
        .scalar()
    ) or 0

    popular = (
        db.session.query(Trek.name, func.count(Booking.id).label('cnt'))
        .join(Booking, Trek.id == Booking.trek_id)
        .filter(Booking.created_at >= start)
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
        .all()
    )

    popular_html = ''.join(
        f'<tr><td>{p[0]}</td><td>{p[1]}</td></tr>' for p in popular
    )
    report_html = f"""<!DOCTYPE html>
<html><head><style>
  body{{font-family:Inter,sans-serif;color:#212529;background:#f8f9fa;padding:2rem;}}
  h1{{color:#012d1d;}} table{{border-collapse:collapse;width:100%;margin-top:1rem;}}
  th,td{{border:1px solid #dee2e6;padding:.5rem .75rem;}}
  th{{background:#1b4332;color:white;}}
</style></head>
<body>
  <h1>SummitPeak — Monthly Trekking Report</h1>
  <h2>{now.strftime('%B %Y')}</h2>
  <ul>
    <li><strong>Treks Created:</strong> {total_treks}</li>
    <li><strong>Total Bookings:</strong> {total_bookings}</li>
    <li><strong>Unique Participants:</strong> {participants}</li>
  </ul>
  <h3>Popular Treks</h3>
  <table><tr><th>Trek Name</th><th>Bookings</th></tr>{popular_html}</table>
</body></html>"""

    admin = User.query.filter_by(role='admin').first()
    print(f'[MONTHLY REPORT] Generated for {now.strftime("%B %Y")}')
    print(f'[MONTHLY REPORT] Would email to: {admin.email if admin else "admin"}')
    print(report_html[:300] + '...')

    return {'status': 'success', 'month': now.strftime('%B %Y'), 'bookings': total_bookings}


# ── Task: Export Booking CSV ───────────────────────────────────────────────────

@celery_app.task(name='tasks.export_booking_csv')
def export_booking_csv(user_id):
    from models import Booking  # Deferred import to prevent circular dependency issues

    # Open the Flask application context so SQLAlchemy knows how to connect to the DB
    with flask_app.app_context():
        try:
            bookings = Booking.query.filter_by(user_id=user_id).all()

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'Booking ID', 'User ID', 'Trek Name', 'Location',
                'Difficulty', 'Booking Status', 'Booking Date',
                'Start Date', 'End Date', 'Payment Status',
            ])
            writer.writeheader()
            
            for b in bookings:
                writer.writerow({
                    'Booking ID': b.id,
                    'User ID': b.user_id,
                    'Trek Name': b.trek.name if b.trek else '',
                    'Location': b.trek.location if b.trek else '',
                    'Difficulty': b.trek.difficulty if b.trek else '',
                    'Booking Status': b.status,
                    'Booking Date': b.booking_date.strftime('%Y-%m-%d') if b.booking_date else '',
                    'Start Date': b.trek.start_date.isoformat() if b.trek and b.trek.start_date else '',
                    'End Date': b.trek.end_date.isoformat() if b.trek and b.trek.end_date else '',
                    'Payment Status': b.payment_status,
                })

            # Retrieve the raw CSV text from the memory buffer
            csv_data_string = output.getvalue()
            
            print(f'[CSV EXPORT SUCCESS] User {user_id}: Prepared {len(bookings)} records in memory.')
            
            # Return the text data. Celery saves this string directly into the Redis Result Backend.
            return csv_data_string

        except Exception as e:
            print(f'[CSV EXPORT ERROR] Failed to generate data for User {user_id}: {str(e)}')
            raise e