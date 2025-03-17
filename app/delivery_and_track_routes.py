from flask import Blueprint, jsonify, request
from app import db

from app.models import Order
from util.helpers import permission_required
delivery_routes = Blueprint('delivery', __name__)


def notify_buyer(order, param):
    pass

# Add a status field to Order (e.g., "Pending", "At Store", "In Transit", "Delivered").
@delivery_routes.route('/orders/<int:order_id>/status', methods=['PUT'])
@permission_required('can_manage_deliveries')
def update_delivery_status(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    if order.delivery_user_id != current_user.id:
        return jsonify({"error": "Not your delivery"}), 403
    data = request.get_json()
    order.status = data['status']
    db.session.commit()
    notify_buyer(order, f"Order status updated to {order.status}")
    return jsonify({"message": "Status updated"}), 200


@customer_routes.route('/orders/<int:order_id>/track', methods=['GET'])
@token_required
def track_order(current_user, order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return jsonify({
        "order_id": order.id,
        "status": order.status,
        "tracking_code": order.tracking_code
    }), 200