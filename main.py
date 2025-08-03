import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

app = ApplicationBuilder().token(TOKEN).build()


# Sample /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Hello, I'm CyberTorch!")


app.add_handler(CommandHandler("start", start))


# Webhook Setup (Render will expose this port via PORT env var)
async def main():
    # Get your external URL (from Render)
    WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"

    await app.bot.set_webhook(WEBHOOK_URL)
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )
    await app.updater.idle()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
