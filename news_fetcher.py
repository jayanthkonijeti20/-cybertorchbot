import time
import feedparser

NEWS_SOURCES = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("Threatpost", "https://threatpost.com/feed/")
]

async def fetch_news():
    news = []
    for name, url in NEWS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                news.append(f"🔹 {name}: <a href='{entry.link}'>{entry.title}</a>")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Error fetching {name}: {str(e)}")
    return news or ["No updates currently available"]
