from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, Order
import uvicorn

app = FastAPI()

@app.post("/webhook/stripe")
async def stripe_webhook(payload: dict, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    order_id = payload.get("data", {}).get("object", {}).get("metadata", {}).get("order_id")
    if not order_id:
        return {"status": "ignored"}
    order = db.query(Order).filter(Order.id == order_id).first()
    if order and payload["type"] == "payment_intent.succeeded":
        order.status = "paid"
        db.commit()
        background_tasks.add_task(notify_user, order.user_id, f"Order #{order_id} paid! Processing now.")
    return {"status": "ok"}

async def notify_user(user_id: int, message: str):
    # For now, this won't work without the bot instance; we'll fix this later if needed
    print(f"Would notify user {user_id}: {message}")

@app.post("/delivery-update")
async def delivery_update(order_id: int, status: str, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        background_tasks.add_task(notify_user, order.user_id, f"Order #{order_id} {status}!")
    return {"status": "updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Only for local testing