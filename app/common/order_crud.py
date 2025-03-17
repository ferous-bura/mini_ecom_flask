from flask import jsonify
from app import db
from app.models import Order, OrderItem, Product, Notification, CartItem


def get_orders(user_id, is_seller=False):
    q = Order.query.join(OrderItem).join(Product).filter(Product.seller_id == user_id) if is_seller else Order.query
    orders = q.all()
    return [{
        "id": o.id,
        "total_amount": o.total_amount,
        "delivery_status": o.delivery_option.name if o.delivery_option else "Pending",
        "payment_status": o.payment_status,
        "items": [{"product_name": oi.product.name, "quantity": oi.quantity} for oi in o.order_items]
    } for o in orders]

def update_delivery_status(user_id, order_id, delivery_option_id, is_seller=False):
    q = Order.query.join(OrderItem).join(Product).filter(Product.seller_id == user_id) if is_seller else Order.query
    order = q.filter_by(id=order_id).first()
    if not order:
        return {"error": "Order not found or not yours"}, 404
    order.delivery_option_id = delivery_option_id
    db.session.commit()
    notification = Notification(
        user_id=order.user_id,
        title="Delivery Update",
        type="delivery_update",
        message=f"Order #{order.id} delivery updated.",
        data={"order_id": order.id, "delivery_status": order.delivery_option.name},
        is_read=False,
        is_sent=False
    )
    db.session.add(notification)
    db.session.commit()
    return {"message": "Delivery updated"}

def create_order_from_cart(user_id, delivery_option_id):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return {"error": "Cart is empty"}, 400
    order = Order(user_id=user_id, total_amount=0, delivery_option_id=delivery_option_id)
    db.session.add(order)
    db.session.flush()
    total = 0
    for item in cart_items:
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
        total += item.product.price * item.quantity
        db.session.add(order_item)
        db.session.delete(item)
    order.total_amount = total + order.delivery_option.base_fee
    db.session.commit()
    return {"message": "Order created", "order_id": order.id}, 201
