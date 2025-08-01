import logging
import feedparser
import requests
import nest_asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import JobQueue

nest_asyncio.apply()

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔐 Replace with your Telegram Bot Token
TOKEN = "8282771504:AAFlaocA6zBCd369Kkz_H60Hp97j9G7LOZU"
CHAT_ID = "967988398"  # Replace this with your Telegram user ID or group ID

# 🌐 Cybersecurity news feeds
FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
    "Bleeping Computer": "https://www.bleepingcomputer.com/feed/",
    "Security Week": "https://feeds.feedburner.com/securityweek",
}

# Store sent article links to avoid duplicates
sent_articles = set()

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
            logger.error(f"[{name}] Failed: {e}")

async def start_command(update, context):
    await update.message.reply_text("👋 Cyber Bot Activated! You'll receive news updates every 10 minutes.")

def main():
    app = Application.builder().token(TOKEN).build()

    # /start command
    app.add_handler(CommandHandler("start", start_command))

    # Schedule job every 10 minutes
    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(send_news, interval=600, first=5)  # 600 seconds = 10 minutes

    logger.info("🤖 Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()
