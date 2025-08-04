import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import feedparser
import time

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

# News sources
SOURCES = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/")
]

def get_news():
    news = []
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # Get 3 latest
                news.append(f"🔹 {name}: {entry.title}\n{entry.link}")
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    return news

# Command handlers
def start(update: Update, context):
    update.message.reply_text("Welcome! Use /latest for news.")

def latest(update: Update, context):
    news = get_news()
    update.message.reply_text("\n\n".join(news) if news else "No updates found.")

# Webhook setup
dispatcher = Dispatcher(bot, None)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("latest", latest))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def health_check():
    return "Bot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
