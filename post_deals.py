import os
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]
TRAVELPAYOUTS_TOKEN = os.environ["TRAVELPAYOUTS_TOKEN"]
AFFILIATE_MARKER = os.environ["AFFILIATE_MARKER"]

CITY_NAMES = {
    "BCN": "Barcelona 🇪🇸", "MAD": "Madrid 🇪🇸", "FCO": "Rome 🇮🇹",
    "MXP": "Milan 🇮🇹", "CDG": "Paris 🇫🇷", "AMS": "Amsterdam 🇳🇱",
    "PRG": "Prague 🇨🇿", "DUB": "Dublin 🇮🇪", "BER": "Berlin 🇩🇪",
    "AGP": "Malaga 🇪🇸", "ALC": "Alicante 🇪🇸", "FAO": "Faro 🇵🇹"
}

def fetch_cheapest_deals(origin="LON"):
    url = f"https://api.travelpayouts.com/v2/prices/latest?currency=gbp&origin={origin}&limit=20&token={TRAVELPAYOUTS_TOKEN}"
    response = requests.get(url).json()
    
    if not response.get("success") or not response.get("data"):
        return []
    
    deals = [d for d in response["data"] if d.get("value", 999) <= 80]
    return sorted(deals, key=lambda x: x["value"])[:3]

def post_to_telegram(deal, origin="LON"):
    dest = deal["destination"]
    dest_name = CITY_NAMES.get(dest, dest)
    price = deal["value"]
    depart_date = deal.get("depart_date", "Flexible")
    return_date = deal.get("return_date", "Flexible")
    
    booking_url = f"https://www.aviasales.com/search/{origin}0110{dest}1?marker={AFFILIATE_MARKER}"
    
    message = (
        f"🚨 **BUDGET ESCAPE FOUND** 🚨\n\n"
        f"✈️ **Route:** London ({origin}) ➔ {dest_name}\n"
        f"💰 **Round-Trip:** £{price:.0f}\n"
        f"📅 **Depart:** {depart_date} | **Return:** {return_date}\n\n"
        f"🔥 *Fares change quickly. Tap below to check availability.*"
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
    print(f"Posted deal to {dest}: Status {res.status_code}")

if __name__ == "__main__":
    deals = fetch_cheapest_deals("LON")
    for deal in deals:
        post_to_telegram(deal, "LON")
