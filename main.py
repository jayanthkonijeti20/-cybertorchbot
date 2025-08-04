import logging
import feedparser
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import os

nest_asyncio.apply()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables from Render
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Example: '@yourchannel' or chat ID like -123456789

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

# Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I will send you the latest cybersecurity news every 10 minutes.")

# Scheduled job to send news
async def send_news(application):
    for url in FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            message = f"🛡️ *{entry.title}*\n{entry.link}"
            try:
                await application.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Failed to send message: {e}")

# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Register command handler
    app.add_handler(CommandHandler("start", start))

    # Scheduler to run news fetching every 10 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_news, trigger='interval', minutes=10, args=[app])
    scheduler.start()

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
