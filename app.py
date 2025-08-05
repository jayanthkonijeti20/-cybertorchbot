import os
from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route('/health', methods=['GET'])
def health_check():
    return '✅ CyberTorchBot is alive!', 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() == "/start":
            send_message(chat_id, "👋 Welcome to *CyberTorchBot*! Type /news to get the latest cybersecurity headlines.", markdown=True)

        elif text.lower() == "/news":
            news = get_latest_news()
            send_message(chat_id, news, markdown=True)

        else:
            send_message(chat_id, "🤖 Unknown command. Try /start or /news.")

    return "OK", 200

def send_message(chat_id, text, markdown=False):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown" if markdown else None
    }
    requests.post(TELEGRAM_API_URL, json=payload)

def get_latest_news():
    headlines = []

    # Scrape The Hacker News
    try:
        thn = requests.get("https://thehackernews.com").text
        soup = BeautifulSoup(thn, "html.parser")
        articles = soup.select(".body-post h2 a")[:3]
        for a in articles:
            title = a.text.strip()
            url = a["href"]
            headlines.append(f"• 🔐 [{title}]({url})")
    except Exception as e:
        headlines.append("⚠️ Failed to fetch from The Hacker News.")

    # Scrape BleepingComputer
    try:
        bc = requests.get("https://www.bleepingcomputer.com").text
        soup = BeautifulSoup(bc, "html.parser")
        articles = soup.select(".bc_latest_news .bc_latest_news_title a")[:3]
        for a in articles:
            title = a.text.strip()
            url = "https://www.bleepingcomputer.com" + a["href"]
            headlines.append(f"• 🛡️ [{title}]({url})")
    except Exception as e:
        headlines.append("⚠️ Failed to fetch from BleepingComputer.")

    return "*📰 Latest Cybersecurity News:*\n" + "\n".join(headlines)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


