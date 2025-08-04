import logging
import feedparser
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import os

nest_asyncio.apply()

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot Token and Chat ID from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Example: '@yourchannel' or your chat ID

# Cybersecurity RSS Feeds
FEEDS = [
    "https://www.darkreading.com/rss.xml",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.securityweek.com/feed/",
    "https://www.zdnet.com/topic/security/rss.xml",
    "https://krebsonsecurity.com/feed/",
    "https://www.cisa.gov/news.xml",
    "https://nakedsecurity.sophos.com/feed/",
    "https://threatpost.com/feed/",
    "https://www.schneier.com/blog/atom.xml"
]

# Send latest news
async def send_news(context):
    for url in FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            message = f"🛡️ *{entry.title}*\n{entry.link}"
            await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I will keep you updated with the latest cybersecurity news!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_news, 'interval', minutes=10, args=[app.bot])
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
