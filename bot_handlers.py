from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database import Order
from payments import create_payment_link, generate_qr_code
from database import SessionLocal  # Import SessionLocal directly
import json

PRODUCTS = {"1": {"name": "T-Shirt", "price": 10.0}, "2": {"name": "Mug", "price": 5.0}}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /shop to browse.")

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("T-Shirt ($10)", callback_data="add_1")],
        [InlineKeyboardButton("Mug ($5)", callback_data="add_2")],
        [InlineKeyboardButton("Checkout", callback_data="checkout")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Pick a product:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Manually create a DB session
    db = SessionLocal()
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        if query.data.startswith("add_"):
            product_id = query.data.split("_")[1]
            cart = context.user_data.get("cart", [])
            cart.append(product_id)
            context.user_data["cart"] = cart
            await query.edit_message_text(f"Added {PRODUCTS[product_id]['name']} to cart. /shop to continue.")

        elif query.data == "checkout":
            if not context.user_data.get("cart"):
                await query.edit_message_text("Cart is empty! Add something with /shop.")
            else:
                await query.edit_message_text("Enter your shipping address:")
                context.user_data["stage"] = "address"
    finally:
        db.close()  # Always close the session

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Manually create a DB session
    db = SessionLocal()
    try:
        user_id = update.message.from_user.id
        if context.user_data.get("stage") == "address":
            address = update.message.text
            cart = context.user_data["cart"]
            total = sum(PRODUCTS[p]["price"] for p in cart)

            order = Order(user_id=user_id, products=json.dumps(cart), address=address)
            db.add(order)
            db.commit()

            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?data=fake-payment-{order.id}&size=200x200"
            await update.message.reply_text(f"Scan to pay ${total}: {qr_url}\n(Reply 'paid' to confirm.)")
            context.user_data["stage"] = "payment"
            context.user_data["order_id"] = order.id

        elif context.user_data.get("stage") == "payment" and update.message.text.lower() == "paid":
            order_id = context.user_data["order_id"]
            order = db.query(Order).filter(Order.id == order_id).first()
            order.status = "paid"
            db.commit()
            await update.message.reply_text(f"Order #{order_id} paid! Processing now.")
            context.user_data.clear()
    finally:
        db.close()  # Always close the session


# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Session):
#     user_id = update.message.from_user.id
#     if context.user_data.get("stage") == "address":
#         address = update.message.text
#         cart = context.user_data["cart"]
#         total = sum(PRODUCTS[p]["price"] for p in cart)

#         order = Order(user_id=user_id, products=json.dumps(cart), address=address)
#         db.add(order)
#         db.commit()

#         payment_url = create_payment_link(total, order.id)
#         qr_url = generate_qr_code(payment_url)
#         await update.message.reply_text(f"Scan to pay ${total}: {qr_url}\nWaiting for confirmation...")
#         context.user_data.clear()
