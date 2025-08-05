import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

# 📰 Dummy news fetcher (replace with your actual logic)
async def fetch_news():
    return [
        "🔐 New zero-day vulnerability discovered in Windows.",
        "🛡️ Cisco releases patch for critical firewall bug.",
        "📡 Hacker group targets financial institutions in Asia."
    ]

# 🚀 /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("✅ /start command received")
        chat_id = update.effective_chat.id
        print(f"💬 Chat ID: {chat_id}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="🛡️ CyberTorchBot is now active!",
            parse_mode="HTML"
        )
    except Exception as e:
        print("❌ Error in /start handler:", str(e))

# 📰 /news command handler
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("✅ /news command received")
        chat_id = update.effective_chat.id
        news_items = await fetch_news()
        await context.bot.send_message(
            chat_id=chat_id,
            text="📡 Latest Cybersecurity News:\n\n" + "\n\n".join(news_items),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        print("❌ Error in /news handler:", str(e))

# 🧠 Main function to run the bot
from telegram.ext import ApplicationBuilder
from telegram.request import HTTPXRequest

def main():
    # ✅ Configure HTTPXRequest with supported arguments
    request = HTTPXRequest()

    application = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=os.environ["WEBHOOK_URL"]
    )


# 🚀 Entry point
if __name__ == "__main__":
    import asyncio
    from telegram import Bot

    async def set_webhook():
        bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        success = await bot.set_webhook("https://cybertorchbot.onrender.com/webhook")
        print("✅ Webhook set:", success)

    asyncio.run(set_webhook())  # Run this once
    main()  # Then start the bot






