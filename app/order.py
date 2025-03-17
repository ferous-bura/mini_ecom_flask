from flask import request, jsonify, Blueprint

from app import db
from .models import User, DeliveryOption, Order, OrderItem, Notification

order_routes = Blueprint('order', __name__)


@order_routes.route('/', methods=['POST'])
def create_order():
    data = request.get_json()
    token = request.headers.get('Authorization').split(' ')[1]  # Bearer token
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    order = Order(
        user_id=user.id,
        total_amount=data['total_amount'],
        delivery_option_id=DeliveryOption.query.filter_by(name=data['delivery_option']).first().id,
        delivery_fee=data['delivery_fee'],
        payment_status=data['payment_status'],
    )
    db.session.add(order)
    db.session.flush()  # Get order ID

    for item in data['cart_items']:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
        )
        db.session.add(order_item)

    # Add notification
    notification = Notification(
        title='New order placed',
        user_id=user.id,
        type='order_placed',
        message=f'Order #{order.id} placed successfully!',
        data={
            'order_id': order.id,
            'products': data['cart_items'],
            'address': data['address'],
            'delivery_option': data['delivery_option'],
            'delivery_fee': data['delivery_fee'],
            'total_amount': data['total_amount'],
            'payment_status': data['payment_status'],
            'created_at': order.created_at.isoformat(),
        },
        is_read=False,
        is_sent=False,
    )
    db.session.add(notification)

    db.session.commit()
    return jsonify({'order_id': order.id}), 201
