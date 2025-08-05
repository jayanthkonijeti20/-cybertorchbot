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

# 📌 Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ CyberTorchBot is now active!")

# 📌 Command: /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_cybersecurity_news()
    await update.message.reply_text(
        f"📡 Latest Cybersecurity News:\n\n{text}",
        disable_web_page_preview=True
    )

# 📌 Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ *CyberTorchBot Help*\n\n"
        "Use the following commands:\n"
        "• /start – Activate the bot\n"
        "• /news – Get the latest cybersecurity headlines\n"
        "• /about – Learn more about this bot\n"
        "• /help – Show this help message",
        parse_mode="Markdown"
    )

# 📌 Command: /about
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 *About CyberTorchBot*\n\n"
        "I’m a Telegram bot built by Jayanth to deliver real-time cybersecurity news "
        "from trusted sources like ThreatPost, KrebsOnSecurity, and The Hacker News.\n\n"
        "Stay informed. Stay secure. 🛡️",
        parse_mode="Markdown"
    )

# 🚀 Build application
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about_command))

# ✅ Run webhook server
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )


