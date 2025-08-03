import os
import logging
import feedparser
import nest_asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

nest_asyncio.apply()

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Environment Variables
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ TOKEN or CHAT_ID not set in environment variables.")

# Cybersecurity RSS Feeds
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
    "The Daily Swig": "https://portswigger.net/daily-swig/rss",
    "Naked Security": "https://nakedsecurity.sophos.com/feed/",
    "Security Affairs": "https://securityaffairs.com/feed",
    "Zero Day": "https://www.zdnet.com/topic/security/rss.xml",
    "CSO Online": "https://www.csoonline.com/index.rss",
    "Help Net Security": "https://www.helpnetsecurity.com/feed/",
    "Malwarebytes Blog": "https://blog.malwarebytes.com/feed/",
    "Cisco Blogs Security": "https://blogs.cisco.com/security/feed"
}

# Track sent articles to avoid duplicates
sent_articles = set()


async def send_news(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    for name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                link = entry.link
                title = entry.title

                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    published_dt = datetime(*published[:6])
                    if published_dt < yesterday:
                        continue
                else:
                    continue

                if link in sent_articles:
                    continue

                sent_articles.add(link)
                message = (
                    f"🛡️ <b>{title}</b>\n"
                    f"<a href='{link}'>Read More</a>\n"
                    f"Source: {name}"
                )

                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                logger.info(f"✅ Sent: {title} | Source: {name}")

        except Exception as e:
            logger.error(f"❌ Error fetching from {name}: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 CyberTorch Activated!\nYou'll receive the latest cybersecurity news every 5 minutes."
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ CyberTorch bot is up and running!")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))

    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(send_news, interval=300, first=5)

    logger.info("🚀 CyberTorch is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
