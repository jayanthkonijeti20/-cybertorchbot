import os
import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔧 Load environment variables
TOKEN       = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT        = int(os.environ.get("PORT", 5000))

# 📰 RSS feeds
RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.darkreading.com/rss.xml",
]

# 🧠 News fetcher
def get_cybersecurity_news() -> str:
    headlines = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            headlines.append(f"📰 {entry.title}\n🔗 {entry.link}")
    return "\n\n".join(headlines)

# 📌 Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ CyberTorchBot is now active!")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_cybersecurity_news()
    await update.message.reply_text(
        f"📡 Latest Cybersecurity News:\n\n{text}",
        disable_web_page_preview=True
    )

# 🚀 Build application
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

# ✅ Run webhook server
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )
