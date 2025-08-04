import logging
import feedparser
import nest_asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

nest_asyncio.apply()

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Telegram chat/channel ID

# RSS feeds
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

# Send news to chat
async def send_news(context: CallbackContext):
    for url in FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            message = f"🛡️ *{entry.title}*\n{entry.link}"
            await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I will keep you updated with the latest cybersecurity news!")

# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_news, trigger='interval', minutes=10, args=[app.bot])
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
