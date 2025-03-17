from flask import jsonify
from app import db
from app.models import DeliveryOption, Order, Notification, User


def register_delivery_user(full_name, email, password):
    user = User(full_name=full_name, email=email, is_seller=False)
    user.set_password(password)
    user.role = "delivery"  # Add a role column to User model
    db.session.add(user)
    db.session.commit()
    return {"message": "Delivery user registered", "user_id": user.id}


def assign_delivery(order_id, delivery_user_id):
    order = Order.query.get_or_404(order_id)
    order.delivery_user_id = delivery_user_id  # Add delivery_user_id to Order model
    db.session.commit()

    # Notify delivery user
    notification = Notification(
        user_id=delivery_user_id,
        title="New Delivery Assignment",
        type="delivery_assignment",
        message=f"You are assigned to deliver Order #{order_id}.",
        data={"order_id": order_id},
        is_read=False,
        is_sent=False
    )
    db.session.add(notification)

    # Notify buyer when delivery arrives at store
    if order.delivery_option.name == "In-Store Pickup":
        buyer_notification = Notification(
            user_id=order.user_id,
            title="In-Store Pickup Ready",
            type="instore_pickup",
            message=f"Your Order #{order_id} is ready for pickup at the store.",
            data={"order_id": order_id, "tracking_code": f"INSTORE-{order_id}"},
            is_read=False,
            is_sent=False
        )
    else:
        buyer_notification = Notification(
            user_id=order.user_id,
            title="Delivery Update",
            type="delivery_tracking",
            message=f"Your Order #{order_id} has arrived at the store. Tracking code: TRACK-{order_id}.",
            data={"order_id": order_id, "tracking_code": f"TRACK-{order_id}"},
            is_read=False,
            is_sent=False
        )
    db.session.add(buyer_notification)
    db.session.commit()
    return {"message": "Delivery assigned", "tracking_code": f"TRACK-{order_id}"}


def get_delivery_options():
    return [{"id": d.id, "name": d.name, "base_fee": d.base_fee} for d in DeliveryOption.query.all()]
