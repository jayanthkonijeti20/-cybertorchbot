import os
import asyncio
from telegram.ext import ApplicationBuilder

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = "https://cybertorchbot.onrender.com/webhook"

async def configure_webhook():
    app = ApplicationBuilder().token(TOKEN).build()
    await app.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set to: {WEBHOOK_URL}")

if __name__ == "__main__":
    asyncio.run(configure_webhook())
