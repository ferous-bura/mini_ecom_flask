# notification_routes.py
from flask import request, jsonify, Blueprint

from app import db
from util.helpers import token_required
from .models import Notification

notification_routes = Blueprint('notification', __name__)



@notification_routes.route('/', methods=['GET'])
@token_required
def get_all_notifications(current_user):
    # Query parameters to control response
    notification_id = request.args.get('id', type=int)  # For detailed view
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if notification_id:  # Detailed view for a single notification
        notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
        if not notification:
            return jsonify({"success": False, "message": "Notification not found"}), 404

        response = {
            "id": notification.id,
            "title": notification.title,
            "type": notification.type,
            "message": notification.message,
            "data": notification.data,
            "is_read": notification.is_read,
            "is_sent": notification.is_sent,
            "created_at": notification.created_at.isoformat()
        }
        return jsonify({"success": True, "notification": response}), 200

    # List view with pagination
    notifications = Notification.query.filter_by(user_id=current_user.id) \
        .order_by(Notification.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    notification_list = [
        {
            "id": n.id,
            "title": n.title,
            "type": n.type,
            "message": n.message,
            "is_read": n.is_read,
            "is_sent": n.is_sent,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications.items
    ]

    return jsonify({
        "success": True,
        "notifications": notification_list,
        "total": notifications.total,
        "pages": notifications.pages,
        "current_page": notifications.page
    }), 200


@notification_routes.route('/update', methods=['POST'])
@token_required
def update_notification_status(current_user):
    data = request.get_json()
    notification_id = data.get('notification_id')
    mark_as_read = data.get('mark_as_read', False)
    mark_as_sent = data.get('mark_as_sent', False)

    if not notification_id:
        return jsonify({"success": False, "message": "Notification ID is required"}), 400

    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if not notification:
        return jsonify({"success": False, "message": "Notification not found"}), 404

    if mark_as_read:
        notification.is_read = True
    if mark_as_sent:
        notification.is_sent = True

    db.session.commit()
    return jsonify({"success": True, "message": "Notification status updated"}), 200


@notification_routes.route('/unsent', methods=['GET'])
@token_required
def get_unsent_notifications(current_user):
    unsent_notifications = Notification.query.filter_by(user_id=current_user.id, is_sent=False) \
        .order_by(Notification.created_at.asc()).all()

    notification_list = [
        {
            "id": n.id,
            "title": n.title,
            "type": n.type,
            "message": n.message,
            "data": n.data,
            "is_read": n.is_read,
            "is_sent": n.is_sent,
            "created_at": n.created_at.isoformat()
        }
        for n in unsent_notifications
    ]

    # Mark as sent only after successful response preparation
    for n in unsent_notifications:
        n.is_sent = True
    db.session.commit()

    return jsonify({
        "success": True,
        "notifications": notification_list,
        "count": len(notification_list)
    }), 200


@notification_routes.route('/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if not notification:
        return jsonify({"success": False, "message": "Notification not found"}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({"success": True, "message": "Notification deleted"}), 200


@notification_routes.route('/all', methods=['DELETE'])
@token_required
def delete_all_notifications(current_user):
    try:
        # Query all notifications for the current user
        notifications = Notification.query.filter_by(user_id=current_user.id).all()

        if not notifications:
            return jsonify({"success": True, "message": "No notifications to delete"}), 200

        # Delete all notifications
        for notification in notifications:
            db.session.delete(notification)

        db.session.commit()

        print(f"Deleted all notifications for user {current_user.id}")  # Debug log
        return jsonify({"success": True, "message": "All notifications deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting notifications: {e}")  # Debug log
        return jsonify({"success": False, "message": "Failed to delete notifications"}), 500
