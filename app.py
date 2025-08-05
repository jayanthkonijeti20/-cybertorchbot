import os
import feedparser
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN       = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.darkreading.com/rss.xml",
]

def get_cybersecurity_news() -> str:
    headlines = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            headlines.append(f"📰 {entry.title}\n🔗 {entry.link}")
    return "\n\n".join(headlines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ CyberTorchBot is now active!")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_cybersecurity_news()
    await update.message.reply_text(
        f"📡 Latest Cybersecurity News:\n\n{text}",
        disable_web_page_preview=True
    )

app = Flask(__name__)
bot = Bot(token=TOKEN)

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

@app.before_first_request
def set_webhook():
    bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set to: {WEBHOOK_URL}")

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
