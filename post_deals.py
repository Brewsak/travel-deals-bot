import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
TRAVELPAYOUTS_TOKEN = os.environ.get("TRAVELPAYOUTS_TOKEN", "").strip()
AFFILIATE_MARKER = os.environ.get("AFFILIATE_MARKER", "").strip()

CITY_NAMES = {
    "BCN": "Barcelona 🇪🇸", "MAD": "Madrid 🇪🇸", "FCO": "Rome 🇮🇹",
    "MXP": "Milan 🇮🇹", "CDG": "Paris 🇫🇷", "AMS": "Amsterdam 🇳🇱",
    "PRG": "Prague 🇨🇿", "DUB": "Dublin 🇮🇪", "BER": "Berlin 🇩🇪",
    "AGP": "Malaga 🇪🇸", "ALC": "Alicante 🇪🇸", "FAO": "Faro 🇵🇹",
    "ATH": "Athens 🇬🇷", "LIS": "Lisbon 🇵🇹", "VIE": "Vienna 🇦🇹",
    "BUD": "Budapest 🇭🇺", "KRK": "Krakow 🇵🇱", "VCE": "Venice 🇮🇹"
}

def fetch_cheapest_deals(origin="LON"):
    url = (
        f"https://api.travelpayouts.com/v2/prices/latest"
        f"?currency=gbp&origin={origin}&period_type=year&limit=30&token={TRAVELPAYOUTS_TOKEN}"
    )
    res = requests.get(url)
    print(f"API HTTP Status: {res.status_code}")
    data = res.json()
    
    if not data.get("success") or not data.get("data"):
        print(f"API response notice: {data}")
        return []
    
    # Sort all returned routes from cheapest to most expensive
    raw_deals = data["data"]
    raw_deals = sorted(raw_deals, key=lambda x: x.get("value", 9999))
    
    # Grab the top 3 lowest priced flights
    top_deals = raw_deals[:3]
    print(f"Found {len(top_deals)} deals to post.")
    return top_deals

def post_to_telegram(deal, origin="LON"):
    dest = deal.get("destination", "EUR")
    dest_name = CITY_NAMES.get(dest, dest)
    price = deal.get("value", 0)
    depart_date = deal.get("depart_date", "Upcoming")
    return_date = deal.get("return_date", "Upcoming")
    
    booking_url = f"https://www.aviasales.com/search/{origin}0110{dest}1?marker={AFFILIATE_MARKER}"
    
    message = (
        f"🚨 *BUDGET ESCAPE FOUND* 🚨\n\n"
        f"✈️ *Route:* London ({origin}) ➔ {dest_name}\n"
        f"💰 *Round-Trip:* £{price:.0f}\n"
        f"📅 *Depart:* {depart_date} | *Return:* {return_date}\n\n"
        f"🔥 _Fares change quickly. Tap below to check availability._"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": f"👉 Book Flight (£{price:.0f})", "url": booking_url}]
            ]
        }
    }
    
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    res = requests.post(send_url, json=payload)
    print(f"Posted to Telegram ({dest}): Status {res.status_code} - {res.text}")

if __name__ == "__main__":
    deals = fetch_cheapest_deals("LON")
    for deal in deals:
        post_to_telegram(deal, "LON")
