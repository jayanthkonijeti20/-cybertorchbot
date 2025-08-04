import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import feedparser
import time

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

# 10+ Cybersecurity News Sources
SOURCES = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("Threatpost", "https://threatpost.com/feed/"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("CSO Online", "https://www.csoonline.com/feed"),
    ("SecurityWeek", "https://feeds.feedburner.com/securityweek"),
    ("GBHackers", "https://gbhackers.com/feed/"),
    ("Cybersecurity Insiders", "https://www.cybersecurity-insiders.com/feed/"),
    ("The Record", "https://therecord.media/feed/")
]

def fetch_news(max_items=3):
    """Fetch headlines without user tracking"""
    news = []
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                news.append(f"🔸 *{name}*: [{entry.title}]({entry.link})")
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"⚠️ Error with {name}: {e}")
    return news[:15]  # Limit to 15 items

# Command: /latest
def latest(update: Update, context):
    news = fetch_news()
    if news:
        update.message.reply_text(
            "📡 *Latest Cybersecurity News:*\n\n" + "\n\n".join(news),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    else:
        update.message.reply_text("❌ No updates found. Try later.")

# Webhook setup
dispatcher = Dispatcher(bot, None)
dispatcher.add_handler(CommandHandler("start", lambda u, _: u.message.reply_text(
    "🛡️ *Cyber News Bot*\nUse /latest to get updates.",
    parse_mode="Markdown"
)))
dispatcher.add_handler(CommandHandler("latest", latest))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
