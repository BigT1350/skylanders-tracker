from main import send_email

fake_result = {
    "title": "Gold Chop Chop Skylander - Rare Collector's Edition",
    "price": "$99.99",
    "link": "https://www.ebay.com/itm/test-gold-chop-chop",
    "price_val": 99.99,
}

reject_link = "https://skylanders-tracker.onrender.com/reject?link=https://www.ebay.com/itm/test-gold-chop-chop"

send_email("gold chop chop", fake_result, reject_link)
