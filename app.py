import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import feedparser  # For RSS feeds
import time  # For rate limiting

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

# Expanded news sources (10+ cybersecurity feeds)
CYBER_NEWS_SOURCES = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("Threatpost", "https://threatpost.com/feed/"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("CSO Online", "https://www.csoonline.com/feed"),
    ("SecurityWeek", "https://feeds.feedburner.com/securityweek"),
    ("GBHackers", "https://gbhackers.com/feed/"),
    ("Cybersecurity Insiders", "https://www.cybersecurity-insiders.com/feed/"),
    ("The Record by Recorded Future", "https://therecord.media/feed/")
]

def get_cyber_news(max_entries=3):
    """Fetch latest headlines from all sources with error handling."""
    news = []
    for name, url in CYBER_NEWS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_entries]:
                news.append(f"🔹 {name}: {entry.title}\n{entry.link}")
            time.sleep(1)  # Avoid overwhelming servers
        except Exception as e:
            print(f"⚠️ Error fetching {name}: {str(e)}")
    return news[:15]  # Return max 15 items to avoid message overflow

# Telegram commands
def start(update: Update, context):
    update.message.reply_text(
        "🛡️ *Cybersecurity News Bot*\n\n"
        "Commands:\n"
        "/start - Show this help\n"
        "/latest - Get recent news\n"
        "/sources - List all news sources",
        parse_mode="Markdown"
    )

def latest(update: Update, context):
    update.message.reply_text("⏳ Fetching latest updates...")
    news = get_cyber_news()
    if news:
        update.message.reply_text(
            "📢 *Latest Cybersecurity News:*\n\n" + "\n\n".join(news),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    else:
        update.message.reply_text("❌ No updates found. Try again later.")

def sources(update: Update, context):
    sources_list = "\n".join([f"• {name}" for name, _ in CYBER_NEWS_SOURCES])
    update.message.reply_text(
        f"📡 *Supported News Sources:*\n\n{sources_list}",
        parse_mode="Markdown"
    )

# Webhook setup
dispatcher = Dispatcher(bot, None)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("latest", latest))
dispatcher.add_handler(CommandHandler("sources", sources))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def health_check():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
