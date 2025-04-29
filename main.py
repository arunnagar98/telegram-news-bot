import os
import time
import requests
import feedparser
from datetime import datetime, timezone
from dotenv import load_dotenv
import telebot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)
last_sent_date = None
last_sent_titles = set()

rss_urls = [
    "https://khabarlahariya.org/feed/",
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://ruralindiaonline.org/rss/hi/",
    "https://www.newslaundry.com/feed"
]

def fetch_news_rss():
    all_news = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                title = entry.title.strip()
                link = entry.link
                description = entry.get("summary", "").strip()

                # Description ko trim karke agar bada hai to use rakhna
                if len(description) < 80:
                    continue  # chhoti descriptions skip karo

                all_news.append((title, link, description))
        except Exception as e:
            print(f"RSS Fetch Error from {url}: {e}")
    return all_news[:6]  # total 6 headlines max

def send_news():
    global last_sent_date, last_sent_titles

    today = datetime.now(timezone.utc).date()

    if last_sent_date == today:
        return

    fresh_news = []
    all_news = fetch_news_rss()

    for title, link, description in all_news:
        if title not in last_sent_titles:
            fresh_news.append((title, link, description))

    if fresh_news:
        message = "📰 *आज की ताज़ा डॉक्यूमेंट्री न्यूज़*:\n\n"
        for title, link, description in fresh_news:
            message += f"• *{title}*\n_{description}_\n[link]({link})\n\n"
            last_sent_titles.add(title)

        bot.send_message(CHAT_ID, message.strip(), parse_mode='Markdown')
        last_sent_date = today
        print("✅ न्यूज़ भेज दी गई।")
    else:
        print("❌ कोई नई न्यूज़ नहीं मिली।")

# ⏰ Daily scheduler: Run at 1:30 AM UTC (7:00 AM IST)
if __name__ == "__main__":
    while True:
        now = datetime.now(timezone.utc)

        if now.hour == 1 and now.minute == 30:
            print("🕒 7:00 AM IST - न्यूज़ भेजी जा रही है...")
            send_news()
            time.sleep(60)
        else:
            time.sleep(20)
