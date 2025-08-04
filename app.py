import os
import asyncio
import time
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import feedparser

# Initialize Flask app
app = Flask(__name__)

# ======================
# CONFIGURATION
# ======================
TOKEN = os.getenv("TELEGRAM_TOKEN")  # From Render environment variables
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = "https://cybertorchbot.onrender.com/webhook"  # Your specific URL

# News sources (customize as needed)
NEWS_SOURCES = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("Threatpost", "https://threatpost.com/feed/"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml")
]

# Initialize Telegram Bot
bot = Bot(token=TOKEN)

# ======================
# NEWS FETCHING LOGIC
# ======================
async def fetch_news(max_items=5):
    """Fetch cybersecurity news with error handling"""
    news = []
    for name, url in NEWS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                news.append(f"🔹 {name}: <a href='{entry.link}'>{entry.title}</a>")
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"⚠️ Failed to fetch {name}: {str(e)}")
    return news or ["No new updates available"]

# ======================
# TELEGRAM COMMANDS
# ======================
async def start(update: Update, context):
    await update.message.reply_text(
        "🛡️ <b>CyberTorch News Bot</b>\n\n"
        "Commands:\n"
        "/start - Show help\n"
        "/news - Get latest updates\n"
        "/sources - List news providers",
        parse_mode="HTML"
    )

async def news(update: Update, context):
    msg = await update.message.reply_text("⏳ Fetching updates...")
    news_items = await fetch_news()
    await bot.edit_message_text(
        text="📡 <b>Latest Cybersecurity News:</b>\n\n" + "\n\n".join(news_items),
        chat_id=update.message.chat_id,
        message_id=msg.message_id,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

async def sources(update: Update, context):
    sources_list = "\n".join([f"• {name}" for name, _ in NEWS_SOURCES])
    await update.message.reply_text(
        f"📚 <b>Supported Sources:</b>\n\n{sources_list}",
        parse_mode="HTML"
    )

# ======================
# FLASK ROUTES
# ======================
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Endpoint for Telegram updates"""
    update = Update.de_json(request.get_json(), bot)
    dispatcher = Dispatcher(bot, None)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("sources", sources))
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "CyberTorch Bot is running ✅", 200

@app.route("/ping")
def ping():
    """Endpoint for uptime monitoring"""
    return "pong", 200

# ======================
# INITIALIZATION
# ======================
async def setup_webhook():
    try:
        await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook configured: {WEBHOOK_URL}")
        print(f"ℹ️ Bot ready at: https://t.me/{bot.get_me().username}")
    except Exception as e:
        print(f"❌ Webhook setup failed: {str(e)}")

if __name__ == "__main__":
    # Configure webhook when running in production
    if "onrender.com" in WEBHOOK_URL:
        asyncio.run(setup_webhook())
    
    # Start Flask app
    app.run(host="0.0.0.0", port=PORT)
