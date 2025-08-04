import logging
import feedparser
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import os

nest_asyncio.apply()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Your Bot Token (use Render Environment Variable instead of hardcoding here)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # Example: '@mychannel' or chat ID

# RSS Feeds
FEEDS = [
    "https://www.darkreading.com/rss.xml",                             # Global security news
    "https://feeds.feedburner.com/TheHackersNews",                    # Hacker News
    "https://www.bleepingcomputer.com/feed/",                         # Malware, ransomware, data breaches
    "https://www.securityweek.com/feed/",                             # Global enterprise security
    "https://www.zdnet.com/topic/security/rss.xml",                   # Tech and security insights
    "https://krebsonsecurity.com/feed/",                              # In-depth security investigations
    "https://www.cisa.gov/news.xml",                                  # US Gov alerts (CISA)
    "https://nakedsecurity.sophos.com/feed/",                         # Sophos blog
    "https://threatpost.com/feed/",                                   # Threat intelligence
    "https://www.schneier.com/blog/atom.xml"                          # Bruce Schneier's security blog
]


# Send latest feed entries
async def send_news(context: CallbackContext):
    for url in FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            message = f"🛡️ *{entry.title}*\n{entry.link}"
            await context.bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")

# Bot command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I will keep you updated with the latest cybersecurity news!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handler
    app.add_handler(CommandHandler("start", start))

    # Scheduler for periodic updates
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_news, trigger='interval', minutes=10, args=[app.bot])
    scheduler.start()

    # Start bot
    app.run_polling()

if __name__ == "__main__":
    main()
