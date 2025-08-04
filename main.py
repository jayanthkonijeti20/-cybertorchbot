import logging
import feedparser
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import os
import asyncio

nest_asyncio.apply()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load secrets from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Chat ID or Channel username

# RSS Feed URLs
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

# News sending function
async def send_news(context: ContextTypes.DEFAULT_TYPE):
    for url in FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            message = f"🛡️ *{entry.title}*\n{entry.link}"
            await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I will keep you updated with the latest cybersecurity news!")

# Main entry
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Schedule job every 10 minutes
    job_queue = app.job_queue
    job_queue.run_repeating(send_news, interval=600, first=10)

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
