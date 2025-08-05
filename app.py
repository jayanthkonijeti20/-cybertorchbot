import os
import feedparser
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    Dispatcher,
)

# 🔐 Load environment variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://cybertorchbot.onrender.com/webhook

# 🌐 Cybersecurity RSS feeds
RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.darkreading.com/rss.xml"
]

# 📰 Fetch cybersecurity news
def get_cybersecurity_news():
    headlines = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:  # Top 2 from each source
            title = entry.title
            link = entry.link
            headlines.append(f"📰 {title}\n🔗 {link}")
    return "\n\n".join(headlines)

# 🚀 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ CyberTorchBot is now active!")

# 📰 /news command
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_text = get_cybersecurity_news()
    await update.message.reply_text(f"📡 Latest Cybersecurity News:\n\n{news_text}", disable_web_page_preview=True)

# 🧠 Flask app setup
app = Flask(__name__)
bot = Bot(token=TOKEN)

# 🧠 Telegram application and dispatcher
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

# 🔗 Telegram webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "OK", 200

# 🔗 Set webhook on startup
@app.before_first_request
def set_webhook():
    bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set to: {WEBHOOK_URL}")

# 🚀 Gunicorn entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
