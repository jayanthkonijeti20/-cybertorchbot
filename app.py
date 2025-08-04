import os
import asyncio
import time
import feedparser
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

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
application = ApplicationBuilder().token(TOKEN).build()

async def fetch_news():
    """Fetch cybersecurity news with error handling"""
    news = []
    for name, url in NEWS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                news.append(f"🔹 {name}: <a href='{entry.link}'>{entry.title}</a>")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Error fetching {name}: {str(e)}")
    return news or ["No updates currently available"]

# Command handlers
async def start(update: Update, context):
    await update.message.reply_text(
        "🛡️ <b>CyberTorch News Bot</b>\n\n"
        "Commands:\n"
        "/start - Show help\n"
        "/news - Get latest updates",
        parse_mode="HTML"
    )

async def news(update: Update, context):
    news_items = await fetch_news()
    await update.message.reply_text(
        "📡 <b>Latest Cybersecurity News:</b>\n\n" + "\n\n".join(news_items),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    asyncio.run(application.process_update(update))
    return jsonify({"status": "ok"}), 200

# Health check
@app.route("/")
def health_check():
    return "🟢 CyberTorch Bot is operational", 200

if __name__ == "__main__":
    async def configure_webhook():
        await application.bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook configured: {WEBHOOK_URL}")
    asyncio.run(configure_webhook())
    app.run(host="0.0.0.0", port=PORT)
