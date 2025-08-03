import os
import logging
import feedparser
import nest_asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

# Apply nest_asyncio for async event loop support on Render
nest_asyncio.apply()

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables (from Render settings)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ TOKEN or CHAT_ID not set in environment variables.")

# Cybersecurity RSS Feeds (15 top sources)
FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
    "Bleeping Computer": "https://www.bleepingcomputer.com/feed/",
    "Security Week": "https://feeds.feedburner.com/securityweek",
    "Dark Reading": "https://www.darkreading.com/rss.xml",
    "Threatpost": "https://threatpost.com/feed/",
    "CyberScoop": "https://www.cyberscoop.com/feed/",
    "SC Media": "https://www.scmagazine.com/home/feed/",
    "HackRead": "https://www.hackread.com/feed/",
    "GovInfoSecurity": "https://www.govinfosecurity.com/rss",
    "Infosecurity Magazine": "https://www.infosecurity-magazine.com/rss/news/",
    "The Daily Swig (PortSwigger)": "https://portswigger.net/daily-swig/rss",
    "Naked Security by Sophos": "https://nakedsecurity.sophos.com/feed/",
    "Security Affairs": "https://securityaffairs.com/feed",
    "Help Net Security": "https://www.helpnetsecurity.com/feed/",
}

# Track sent articles to avoid duplicates
sent_articles = set()


async def send_news(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    for name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # Limit to latest 5 per feed
                link = entry.link
                title = entry.title

                # Parse date
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    published_dt = datetime(*published[:6])
                    if published_dt < yesterday:
                        continue
                else:
                    continue  # Skip if no timestamp

                if link in sent_articles:
                    continue

                sent_articles.add(link)

                message = (
                    f"📰 <b>{title}</b>\n"
                    f"Source: {name}\n\n"
                    f"<a href='{link}'>Read More</a>"
                )
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"❌ Error fetching from {name}: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 CyberTorch Activated!\nYou'll receive cybersecurity news every 5 minutes from top sources."
    )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))

    # Schedule job every 5 minutes
    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(send_news, interval=300, first=5)

    logger.info("🚀 CyberTorch is now running...")
    app.run_polling()


if __name__ == "__main__":
    main()
