from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from telegram.ext import Application
from bot_handlers import start, shop, button, handle_message
from database import get_db, Order
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import uvicorn

app = FastAPI()
telegram_app = Application.builder().token("7974258002:AAEpZeM3aAN07lOvjim07qMGPrSmiedZw3A").build()

# https://t.me/DynamicChewataBot

# Register handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("shop", shop))
telegram_app.add_handler(CallbackQueryHandler(button))
telegram_app.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.on_event("startup")
async def startup_event():
    telegram_app.initialize()
    telegram_app.start()
    await telegram_app.updater.start_polling()

@app.on_event("shutdown")
async def shutdown_event():
    await telegram_app.updater.stop()
    telegram_app.stop()

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
    await telegram_app.bot.send_message(chat_id=user_id, text=message)

@app.post("/delivery-update")
async def delivery_update(order_id: int, status: str, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        background_tasks.add_task(notify_user, order.user_id, f"Order #{order_id} {status}!")
    return {"status": "updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)