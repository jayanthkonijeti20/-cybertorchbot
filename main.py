import os
import logging
import feedparser
import requests
import nest_asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

# Apply patch for async environments (like Railway)
nest_asyncio.apply()

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Get secrets from environment variables
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Build bot application
app = Application.builder().token(TOKEN).build()

# 🌐 Cybersecurity news RSS feeds
FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
    "Bleeping Computer": "https://www.bleepingcomputer.com/feed/",
    "Security Week": "https://feeds.feedburner.com/securityweek",
}

# Track sent articles to prevent duplicates
sent_articles = set()

# 📢 Function to fetch and send latest news
async def send_news(context: ContextTypes.DEFAULT_TYPE):
    for name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # Top 3 from each source
                if entry.link not in sent_articles:
                    sent_articles.add(entry.link)
                    message = f"📰 <b>{entry.title}</b>\nSource: {name}\n\n<a href='{entry.link}'>Read More</a>"
                    await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"[{name}] Error fetching feed: {e}")

# 👋 Respond to /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Cyber Bot Activated! You'll get fresh news every 10 minutes.")

# 🚀 Bot entry point
def main():
    logger.info("🚀 Starting Cyber News Bot on Railway...")

    app.add_handler(CommandHandler("start", start_command))

    # Run news job every 10 minutes
    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(send_news, interval=600, first=5)

    logger.info("🤖 Bot polling started.")
    app.run_polling()

if __name__ == '__main__':
    main()
