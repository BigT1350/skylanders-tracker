import os
import re
import smtplib
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ✉️ Email Setup
sender_email = "gertbimbanos1350@gmail.com"
app_password = "ptovezdiebowsond"
receiver_email = "gertbimbanos1350@gmail.com"

# 🎯 Skylanders list
skylanders = [
    {"name": "chrome spyro", "max_price": 250, "keywords": ["chrome", "spyro", "skylander"]},
    {"name": "crystal clear cynder", "max_price": 250, "keywords": ["crystal", "clear", "cynder", "skylander"]},
    {"name": "crystal clear stealth elf", "max_price": 250, "keywords": ["crystal", "clear", "elf", "skylander"]},
    {"name": "crystal clear wham-shell", "max_price": 250, "keywords": ["crystal", "clear", "wham", "skylander"]},
    {"name": "crystal clear whirlwind", "max_price": 250, "keywords": ["crystal", "clear", "whirlwind", "skylander"]},
    {"name": "flocked stump smash", "max_price": 100, "keywords": ["flocked", "stump", "skylander"]},
    {"name": "glow in the dark warnado", "max_price": 250, "keywords": ["glow", "dark", "warnado", "skylander"]},
    {"name": "glow in the dark wrecking ball", "max_price": 250, "keywords": ["glow", "dark", "wrecking", "skylander"]},
    {"name": "glow in the dark zap", "max_price": 250, "keywords": ["glow", "dark", "zap", "skylander"]},
    {"name": "gold chop chop", "max_price": 250, "keywords": ["gold", "chop", "skylander", "spyro"]},
    {"name": "gold drill sergeant", "max_price": 250, "keywords": ["gold", "drill", "skylander", "spyro"]},
    {"name": "gold flameslinger", "max_price": 250, "keywords": ["gold", "flame", "skylander", "spyro"]},
    {"name": "metallic purple cynder", "max_price": 250, "keywords": ["purple", "cynder", "metallic", "skylander", "spyro"]},
    {"name": "pearl hex", "max_price": 250, "keywords": ["pearl", "hex", "skylander", "spyro"]},
    {"name": "red camo", "max_price": 250, "keywords": ["red", "camo", "skylander", "spyro"]},
    {"name": "silver boomer", "max_price": 250, "keywords": ["silver", "boomer", "skylander"]},
    {"name": "silver dino-rang", "max_price": 250, "keywords": ["silver", "dino", "skylander"]},
    {"name": "silver eruptor", "max_price": 250, "keywords": ["silver", "eruptor", "skylander"]},
]

# 📂 File setup
seen_file = "seen_listings.txt"
rejected_file = "rejected_listings.txt"
for file in [seen_file, rejected_file]:
    if not os.path.exists(file):
        open(file, "w").close()

def load_seen():
    with open(seen_file, "r") as f:
        return set(line.strip() for line in f)

def load_rejected():
    with open(rejected_file, "r") as f:
        return set(line.strip() for line in f)

def save_seen(link):
    with open(seen_file, "a") as f:
        f.write(link + "\n")

# 🕸️ eBay Scraper
import random
import time

def search_ebay(query, max_price, required_keywords):
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=15"
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
        ])
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ eBay returned status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".s-item")

        seen = load_seen()
        rejected = load_rejected()
        results = []

        for item in items:
            title_el = item.select_one(".s-item__title")
            price_el = item.select_one(".s-item__price")
            link_el = item.select_one("a")

            if not (title_el and price_el and link_el):
                continue

            title = title_el.text.lower()
            price_match = re.search(r"\$([\d,.]+)", price_el.text)
            if not price_match:
                continue
            price = float(price_match.group(1).replace(",", ""))
            link = link_el["href"].split("?")[0]

            if (
                "new listing" in title
                or not all(word in title for word in required_keywords)
                or price > max_price
                or link in seen
                or link in rejected
            ):
                continue

            results.append({"title": title_el.text, "price": price_el.text, "link": link, "price_val": price})
        
        # Wait a bit before next request to avoid rate-limiting
        time.sleep(random.uniform(3, 5))
        return results

    except Exception as e:
        print(f"❌ Scrape failed: {e}")
        return []

# 📧 Email sender
def send_email(name, result, reject_link):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔥 Skylanders Match: {result['title']}"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    body = f"""Found a matching Skylander!

🎯 Search: {name}
🧸 {result['title']}
💰 {result['price']}
🔗 {result['link']}

❌ Reject this listing: {reject_link}
"""
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# 🚀 Run the tracker
def run_tracker(public_url):
    for sk in skylanders[:5]:  # Limit to first 5 per run
        print(f"🔍 Searching: {sk['name']}")
        results = search_ebay(sk["name"], sk["max_price"], sk["keywords"])
        if results:
            result = sorted(results, key=lambda r: r["price_val"])[0]
            reject_link = f"{public_url}/reject?link={result['link']}"
            send_email(sk["name"], result, reject_link)
            save_seen(result["link"])
            print(f"✅ Sent: {result['title']}")
        else:
            print("❌ No match found.")

# 🌐 Flask reject server
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Skylanders Tracker is running."

@app.route("/reject")
def reject():
    link = request.args.get("link")
    if not link:
        return "No link provided."

    with open(rejected_file, "a") as f:
        f.write(link.strip() + "\n")
    return f"❌ Rejected: {link}"

# 🔁 Auto-run on startup
if __name__ == "__main__":
    import threading

    def run_flask():
        app.run(host="0.0.0.0", port=10000)

    def run_every_x_minutes():
        import time
        time.sleep(10)  # wait until Flask starts
        while True:
            try:
                public_url = "https://skylanders-tracker.onrender.com"
                run_tracker(public_url)
            except Exception as e:
                print(f"⚠️ Error: {e}")
            time.sleep(3600)  # repeat every hour

    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_every_x_minutes).start()
