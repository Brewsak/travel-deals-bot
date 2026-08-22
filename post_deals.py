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
    # show_to_affiliates=false pulls all globally cached cheap fares
    url = (
        f"https://api.travelpayouts.com/v2/prices/latest"
        f"?currency=gbp&origin={origin}&period_type=year&limit=30&show_to_affiliates=false&token={TRAVELPAYOUTS_TOKEN}"
    )
    res = requests.get(url)
    data = res.json()
    
    if not data.get("success") or not data.get("data"):
        print(f"API returned empty or failed: {data}")
        return []
    
    # Sort from cheapest upwards
    sorted_deals = sorted(data["data"], key=lambda x: x.get("value", 9999))
    return sorted_deals[:3]

def post_to_telegram(deal, origin="LON"):
    dest = deal.get("destination", "EUR")
    dest_name = CITY_NAMES.get(dest, dest)
    price = deal.get("value", 0)
    depart_date = deal.get("depart_date", "Upcoming")
    return_date = deal.get("return_date", "Upcoming")
    
    booking_url = f"https://www.aviasales.com/search/{origin}0110{dest}1?marker={AFFILIATE_MARKER}"
    
    message = (
        f"🚨 <b>BUDGET ESCAPE FOUND</b> 🚨\n\n"
        f"✈️ <b>Route:</b> London ({origin}) ➔ {dest_name}\n"
        f"💰 <b>Round-Trip:</b> £{price:.0f}\n"
        f"📅 <b>Depart:</b> {depart_date} | <b>Return:</b> {return_date}\n\n"
        f"🔥 <i>Fares change quickly. Tap below to check availability.</i>"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": f"👉 Book Flight (£{price:.0f})", "url": booking_url}]
            ]
        }
    }
    
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    res = requests.post(send_url, json=payload)
    print(f"Posted {dest}: Response {res.status_code} - {res.text}")

if __name__ == "__main__":
    deals = fetch_cheapest_deals("LON")
    print(f"Fetched {len(deals)} deals.")
    for deal in deals:
        post_to_telegram(deal, "LON")
