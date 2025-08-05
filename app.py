import os
import asyncio
import feedparser
import httpx
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

# 🌐 Cybersecurity RSS feeds
RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.darkreading.com/rss.xml"
]

# 📰 Fetch real cybersecurity news
async def fetch_news():
    headlines = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:  # Top 2 from each source
            title = entry.title
            link = entry.link
            headlines.append(f"📰 {title}\n🔗 {link}")
    return headlines

# 🚀 /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("✅ /start command received")
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text="🛡️ CyberTorchBot is now active!",
            parse_mode="HTML"
        )
    except Exception as e:
        print("❌ Error in /start handler:", str(e))

# 📰 /news command handler
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("✅ /news command received")
        chat_id = update.effective_chat.id
        news_items = await fetch_news()
        await context.bot.send_message(
            chat_id=chat_id,
            text="📡 Latest Cybersecurity News:\n\n" + "\n\n".join(news_items),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        print("❌ Error in /news handler:", str(e))

# 🔗 Set webhook
async def configure_webhook():
    bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
    success = await bot.set_webhook(os.environ["WEBHOOK_URL"])
    print(f"✅ Webhook set:", success)

# 🧠 Main function to run the bot
def main():
    request = HTTPXRequest()
    application = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=os.environ["WEBHOOK_URL"]
    )

# 🚀 Entry point
async def run_bot():
    await configure_webhook()
    main()

if __name__ == "__main__":
    asyncio.run(run_bot())
