import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from news_fetcher import fetch_news  # Modular news logic

# Initialize Flask app
app = Flask(__name__)

# Load bot token from environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = "https://cybertorchbot.onrender.com/webhook"  # Update if needed

if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN environment variable not set!")

# Initialize Telegram bot application
application = ApplicationBuilder().token(TOKEN).build()

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

# 🔗 Telegram webhook endpoint
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    asyncio.run(application.process_update(update))
    return jsonify({"status": "ok"}), 200

# ✅ Health check endpoint
@app.route("/", methods=["GET"])
def health_check():
    return "🟢 CyberTorch Bot is operational", 200
