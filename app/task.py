# models.py
from datetime import datetime, timedelta

from app import db
from app.models import Notification


class User(db.Model):
    # Add to existing User model
    device_token = db.Column(db.String(255), nullable=True)  # For FCM push notifications


# Add to a cron job or Flask scheduler
def cleanup_notifications():
    threshold = datetime.utcnow() - timedelta(days=30)
    Notification.query.filter(Notification.created_at < threshold).delete()
    db.session.commit()
