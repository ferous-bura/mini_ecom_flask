from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from database import get_db, Order

app = Flask(__name__)

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_json()
    order_id = payload.get("data", {}).get("object", {}).get("metadata", {}).get("order_id")
    if not order_id:
        return jsonify({"status": "ignored"})
    
    db: Session = next(get_db())
    order = db.query(Order).filter(Order.id == order_id).first()
    if order and payload["type"] == "payment_intent.succeeded":
        order.status = "paid"
        db.commit()
        # Notify user logic can be added here
    return jsonify({"status": "ok"})

@app.route("/delivery-update", methods=["POST"])
def delivery_update():
    data = request.get_json()
    order_id = data.get("order_id")
    status = data.get("status")
    
    db: Session = next(get_db())
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        # Notify user logic can be added here
    return jsonify({"status": "updated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)  # Only for local testing

# source ~/Desktop/myenv/bin/activate
