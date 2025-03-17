from flask import jsonify, Blueprint

from app import db
from app.models import CartItem, OrderItem, Address, Notification, Order
from util.helpers import token_required

checkout_routes = Blueprint('checkout', __name__)


@checkout_routes.route('/', methods=['POST'])
@token_required
def checkout(current_user):
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        return jsonify({"message": "Your cart is empty, please add items before checkout."}), 400

    # Create new Order
    new_order = Order(user_id=current_user.id, approved=True)
    db.session.add(new_order)
    db.session.flush()

    # Transfer cart items to order
    total_amount = 0
    order_items_data = []
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        total_amount += item.quantity * item.product.price
        db.session.add(order_item)
        db.session.delete(item)
        order_items_data.append({
            "product_id": item.product_id,
            "name": item.product.name,
            "quantity": item.quantity,
            "price": item.product.price,
            "total": item.quantity * item.product.price
        })

    # Set total amount
    new_order.total_amount = total_amount

    # Get user's address (assuming the latest address is used for simplicity)
    address = Address.query.filter_by(user_id=current_user.id).order_by(Address.id.desc()).first()
    address_text = address.address if address else "No address provided"

    # Create a detailed notification
    notification_data = {
        "order_id": new_order.id,
        "products": order_items_data,
        "address": address_text,
        "delivery_option": new_order.delivery_option.name if new_order.delivery_option else "Not specified",
        "delivery_fee": new_order.delivery_fee,
        "payment_status": new_order.payment_status,
        "total_amount": new_order.total_amount,
        "created_at": new_order.created_at.isoformat()
    }

    notification = Notification(
        title="New order placed",
        user_id=current_user.id,
        type="order_placed",
        message=f"Order #{new_order.id} placed successfully!",
        data=notification_data,
        is_read=False,
        is_sent=False
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Order successfully placed.",
        "order_id": new_order.id
    }), 200
