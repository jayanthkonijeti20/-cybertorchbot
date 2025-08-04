import os
import asyncio
import time
import feedparser
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Initialize Flask app
app = Flask(__name__)

# Load configuration from environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = "https://cybertorchbot.onrender.com/webhook"  # Update if needed

if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN environment variable not set!")

# News sources
NEWS_SOURCES = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("Threatpost", "https://threatpost.com/feed/")
]

# Initialize Telegram bot application
application = ApplicationBuilder().token(TOKEN).build()

# 📰 Fetch cybersecurity news
async def fetch_news():
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

# 📌 /start command
async def start(update: Update, context):
    await update.message.reply_text(
        "🛡️ <b>CyberTorch News Bot</b>\n\n"
        "Commands:\n"
        "/start - Show help\n"
        "/news - Get latest updates",
        parse_mode="HTML"
    )

# 📰 /news command
async def news(update: Update, context):
    news_items = await fetch_news()
    await update.message.reply_text(
        "📡 <b>Latest Cybersecurity News:</b>\n\n" + "\n\n".join(news_items),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# Register command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

# 🔗 Webhook endpoint for Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    asyncio.run(application.process_update(update))
    return jsonify({"status": "ok"}), 200

# ✅ Health check endpoint
@app.route("/", methods=["GET"])
def health_check():
    return "🟢 CyberTorch Bot is operational", 200

# 🚀 Configure webhook and run Flask app
if __name__ == "__main__":
    async def configure_webhook():
        await application.bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook configured: {WEBHOOK_URL}")

    asyncio.run(configure_webhook())
    app.run(host="0.0.0.0", port=PORT)
