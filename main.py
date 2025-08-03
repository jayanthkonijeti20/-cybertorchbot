import os
import logging
import feedparser
from telegram import Bot
from telegram.constants import ParseMode
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Initialize the bot
bot = Bot(token=TOKEN)

# Define RSS feed URLs
RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://krebsonsecurity.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://www.cyberscoop.com/feed/",
    "https://threatpost.com/feed/",
    "https://feeds.feedburner.com/securityweek",
    "https://www.infosecurity-magazine.com/rss/news/",
    "https://medium.com/feed/mitre-attack",
    "https://nakedsecurity.sophos.com/feed/"
]

# Function to fetch and send news
def send_news():
    all_entries = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)

    # Sort by published date if available
    all_entries = sorted(
        all_entries, key=lambda x: x.get("published_parsed", datetime.utcnow()), reverse=True
    )

    # Get top 5 recent news
    top_news = all_entries[:5]

    for entry in top_news:
        title = entry.title
        link = entry.link
        message = f"🛡️ <b>{title}</b>\n<a href='{link}'>Read more</a>"
        try:
            bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

# Scheduler to send news every 5 hours
scheduler = BackgroundScheduler()
scheduler.add_job(send_news, 'interval', hours=5)
scheduler.start()

# Run once at startup
send_news()

# Keep the app running
import time
while True:
    time.sleep(60)
