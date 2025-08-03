import os
import logging
import feedparser
import nest_asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

nest_asyncio.apply()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# List of RSS feeds
RSS_FEEDS = [
    "https://www.darkreading.com/rss.xml",
    "https://www.securityweek.com/feed/",
    "https://threatpost.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.schneier.com/feed/atom/"
]

CHAT_ID = os.getenv("CHAT_ID")  # Set this in Render if needed
TOKEN = os.getenv("BOT_TOKEN")  # Set this in Render

sent_articles = set()


async def send_news(context: ContextTypes.DEFAULT_TYPE):
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:
            if entry.link not in sent_articles:
                message = f"*{entry.title}*\n{entry.link}"
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='Markdown'
                )
                logging.info(f"Sent: {entry.link}")
                sent_articles.add(entry.link)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ CyberTorch Bot is alive and running!")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("status", status))

    # Setup scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_news, "interval", minutes=30, args=[app.bot])
    scheduler.start()

    logging.info("Bot started.")
    app.run_polling()


if __name__ == "__main__":
    main()
