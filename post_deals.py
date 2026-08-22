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
    "BUD": "Budapest 🇭🇺", "KRK": "Krakow 🇵🇱", "VCE": "Venice 🇮🇹",
    "PMI": "Mallorca 🇪🇸", "IBZ": "Ibiza 🇪🇸", "OPO": "Porto 🇵🇹"
}

def fetch_cheapest_deals():
    # Uses the primary Travelpayouts v3 live flight deals endpoint
    url = (
        f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
        f"?origin=LON&currency=gbp&unique=false&sorting=price&limit=15&token={TRAVELPAYOUTS_TOKEN}"
    )
    res = requests.get(url)
    data = res.json()
    
    if not data.get("success") or not data.get("data"):
        # Fallback to direct latest feed
        fallback_url = f"https://api.travelpayouts.com/v2/prices/latest?currency=gbp&origin=LON&limit=15&show_to_affiliates=false&token={TRAVELPAYOUTS_TOKEN}"
        f_res = requests.get(fallback_url)
        return f_res.json().get("data", [])[:3]
        
    return data["data"][:3]

def post_to_telegram(deal):
    dest = deal.get("destination", "EUR")
    dest_name = CITY_NAMES.get(dest, dest)
    price = deal.get("price") or deal.get("value", 0)
    depart_date = deal.get("departure_at", deal.get("depart_date", "Upcoming"))[:10]
    return_date = deal.get("return_at", deal.get("return_date", "Flexible"))[:10]
    
    booking_url = f"https://www.aviasales.com/search/LON0110{dest}1?marker={AFFILIATE_MARKER}"
    
    message = (
        f"🚨 <b>BUDGET ESCAPE FOUND</b> 🚨\n\n"
        f"✈️ <b>Route:</b> London (LON) ➔ {dest_name}\n"
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
    print(f"Post result: {res.status_code} - {res.text}")

if __name__ == "__main__":
    deals = fetch_cheapest_deals()
    for deal in deals:
        post_to_telegram(deal)
