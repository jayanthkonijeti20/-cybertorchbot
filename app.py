import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler
import feedparser
import time

app = Flask(__name__)

# Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = "https://cybertorchbot.onrender.com/webhook"

# News sources
NEWS_SOURCES = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("Threatpost", "https://threatpost.com/feed/")
]

# Initialize Telegram Bot
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

async def fetch_news():
    """Fetch cybersecurity news"""
    news = []
    for name, url in NEWS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                news.append(f"🔹 {name}: {entry.title}\n{entry.link}")
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching {name}: {str(e)}")
    return news or ["No updates available"]

async def start(update: Update, context):
    await update.message.reply_text(
        "🛡️ CyberTorch News Bot\n\n"
        "Commands:\n"
        "/start - Show help\n"
        "/news - Get updates"
    )

async def news(update: Update, context):
    news_items = await fetch_news()
    await update.message.reply_text("\n\n".join(news_items))

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

@app.route("/webhook", methods=["POST"])
async def webhook():
    json_data = await request.get_json()
    update = Update.de_json(json_data, application.bot)
    await application.process_update(update)
    return "OK", 200

@app.route("/")
def health_check():
    return "Bot is running", 200

if __name__ == "__main__":
    # Set webhook in production
    if "onrender.com" in WEBHOOK_URL:
        async def configure_webhook():
            await application.bot.set_webhook(WEBHOOK_URL)
            print(f"Webhook set to: {WEBHOOK_URL}")
        asyncio.run(configure_webhook())
    
    app.run(host="0.0.0.0", port=PORT)
