from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Telegram bot token from BotFather
TOKEN = "your-telegram-token"

# Payment provider (example)
PAYMENT_API = "https://third-party-payment.com/api/qr"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /shop to see products.")

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pick a product: 1) T-Shirt ($10) 2) Mug ($5)")

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your shipping address:")
    context.user_data["stage"] = "address"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("stage") == "address":
        address = update.message.text
        context.user_data["address"] = address
        # Fake payment QR (replace with real API call)
        qr_url = requests.post(PAYMENT_API, json={"amount": 10}).json()["qr_url"]
        await update.message.reply_text(f"Scan to pay: {qr_url}")
        # In reality, wait for webhook to confirm payment

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("checkout", checkout))
    app.add_handler(MessageHandler(None, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()