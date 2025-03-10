from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handlers import start, shop, button, handle_message

telegram_app = Application.builder().token("7769407638:AAGbEDQUvycuomAjWEuR5ELHnzTllxLT7GQ").build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("shop", shop))
telegram_app.add_handler(CallbackQueryHandler(button))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def main():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    print("Bot is running... Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await telegram_app.updater.stop()
        await telegram_app.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())