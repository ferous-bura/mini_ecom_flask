from flask import jsonify
from .. import db
from ..models import Order, Notification
from datetime import datetime

def process_payment(order_id, payment_status):
    order = Order.query.get_or_404(order_id)
    if payment_status not in ["Pending", "Paid", "Failed"]:
        return {"error": "Invalid payment status"}, 400
    order.payment_status = payment_status
    if payment_status == "Paid":
        notification = Notification(
            user_id=order.user_id,
            title="Payment Successful",
            type="payment_success",
            message=f"Payment for Order #{order_id} completed successfully!",
            data={
                "order_id": order_id,
                "total_amount": order.total_amount,
                "timestamp": datetime.utcnow().isoformat()
            },
            is_read=False,
            is_sent=False
        )
        db.session.add(notification)
    db.session.commit()
    return {"message": f"Payment status updated to {payment_status}"}

import stripe
stripe.api_key = "your-stripe-secret-key"

def process_payment(order_id, payment_method_id):
    order = Order.query.get_or_404(order_id)
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Convert to cents
            currency="usd",
            payment_method=payment_method_id,
            confirmation_method="manual",
            confirm=True
        )
        order.payment_status = "Paid" if payment_intent.status == "succeeded" else "Failed"
        db.session.commit()
        if order.payment_status == "Paid":
            notify_buyer(order, "Payment successful!")
        return {"message": f"Payment {order.payment_status.lower()}"}, 200
    except stripe.error.StripeError as e:
        order.payment_status = "Failed"
        db.session.commit()
        return {"error": str(e)}, 400