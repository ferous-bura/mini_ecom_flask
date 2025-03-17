import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

from util.utils import TELEGRAM_TOKEN

import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler
import smtplib
from email.mime.text import MIMEText

# Replace with your bot token and app URL
APP_DEEP_LINK = "mini64://verify?code="  # Your app's deep link scheme
EMAIL_SENDER = "buraman@hotmail.com"
EMAIL_PASSWORD = "Lmnferous,1"  # Use an app-specific password if using Gmail

# Simulated database (replace with your actual backend)
users_db = {}  # {telegram_id: {"email": str, "code": str, "verified": bool}}

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

async def start(update: Update, context: CallbackContext) -> None:
    # Ask for confirmation method
    keyboard = [
        [InlineKeyboardButton("Register", callback_data="register")],
        [InlineKeyboardButton("Login", callback_data="login")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome, if new register else login", reply_markup=reply_markup)

async def register(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in users_db and users_db[user_id]["verified"]:
        await update.message.reply_text("You’re already registered and verified!")
        return

    # Ask for confirmation method
    keyboard = [
        [InlineKeyboardButton("Telegram", callback_data="telegram")],
        [InlineKeyboardButton("Email", callback_data="email")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("How would you like to receive your confirmation code?", reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data

    if choice == "telegram":
        code = generate_code()
        users_db[user_id] = {"email": None, "code": code, "verified": False}
        keyboard = [[InlineKeyboardButton(f"Confirm: {code}", url=f"{APP_DEEP_LINK}{code}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Your confirmation code is: {code}. Click below to verify:",
            reply_markup=reply_markup
        )
    elif choice == "email":
        await query.edit_message_text("Please send your email address with /email <your-email>")

async def handle_email(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Usage: /email <your-email>")
        return

    email = context.args[0]
    code = generate_code()
    users_db[user_id] = {"email": email, "code": code, "verified": False}

    # Send email
    msg = MIMEText(f"Your confirmation code is: {code}\nOpen your app to verify.")
    msg["Subject"] = "Confirm Your Registration"
    msg["From"] = EMAIL_SENDER
    msg["To"] = email

    with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, email, msg.as_string())

    await update.message.reply_text(f"Code sent to {email}. Send it back here to confirm, or open the app and enter it.")

async def verify_code(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    message = update.message.text

    if user_id not in users_db:
        await update.message.reply_text("Please register first with /register.")
        return

    user_data = users_db[user_id]
    if message == user_data["code"]:
        users_db[user_id]["verified"] = True
        await update.message.reply_text(
            "Verification successful! Click here to open the app:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open App", url=f"{APP_DEEP_LINK}{message}")]])
        )
    else:
        await update.message.reply_text("Invalid code. Try again.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("email", handle_email))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verify_code))
    application.run_polling()

if __name__ == "__main__":
    print("Bot is running... Press Ctrl+C to stop.")
    main()
