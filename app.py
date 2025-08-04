import os
import asyncio
import time
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import feedparser

# Initialize Flask app
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

async def fetch_news(max_items=3):
    """Fetch cybersecurity news"""
    news = []
    for name, url in NEWS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                news.append(f"🔹 {name}: <a href='{entry.link}'>{entry.title}</a>")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Error fetching {name}: {str(e)}")
    return news or ["No updates available"]

# Telegram commands
async def start(update: Update, context):
    await update.message.reply_text(
        "🛡️ <b>CyberTorch Bot</b>\n\n"
        "Commands:\n"
        "/start - Show help\n"
        "/news - Get updates\n"
        "/sources - List providers",
        parse_mode="HTML"
    )

async def news(update: Update, context):
    news_items = await fetch_news()
    await update.message.reply_text(
        "📡 <b>Latest News:</b>\n\n" + "\n\n".join(news_items),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

async def sources(update: Update, context):
    sources_list = "\n".join([f"• {name}" for name, _ in NEWS_SOURCES])
    await update.message.reply_text(
        f"📚 <b>News Sources:</b>\n\n{sources_list}",
        parse_mode="HTML"
    )

# Flask routes
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher = Dispatcher(bot, None)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("sources", sources))
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def health_check():
    return "🟢 CyberTorch Bot is running", 200

@app.route("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    # Configure webhook in production
    if "onrender.com" in WEBHOOK_URL:
        async def setup():
            await bot.set_webhook(WEBHOOK_URL)
            print(f"✅ Webhook set: {WEBHOOK_URL}")
        asyncio.run(setup())
    
    app.run(host="0.0.0.0", port=PORT)
