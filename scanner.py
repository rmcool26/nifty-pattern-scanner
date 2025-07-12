import yfinance as yf
import pandas as pd

import requests

TELEGRAM_TOKEN = '8077075856:AAEsXisqnXbT-UF6YoljZnJ6-8P8a6cCEb0'
TELEGRAM_CHAT_ID = '7492825690'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")


nifty50_symbols = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ITC.NS',
    'AXISBANK.NS', 'LT.NS', 'ASIANPAINT.NS', 'BAJFINANCE.NS', 'HCLTECH.NS',
    'WIPRO.NS', 'MARUTI.NS', 'NESTLEIND.NS', 'ULTRACEMCO.NS', 'SUNPHARMA.NS',
    'TECHM.NS', 'TITAN.NS', 'POWERGRID.NS', 'NTPC.NS', 'ONGC.NS',
    'COALINDIA.NS', 'BAJAJ-AUTO.NS', 'ADANIENT.NS', 'TATAMOTORS.NS', 'GRASIM.NS',
    'HDFCLIFE.NS', 'SBILIFE.NS', 'CIPLA.NS', 'HINDALCO.NS', 'BPCL.NS',
    'DIVISLAB.NS', 'BAJAJFINSV.NS', 'DRREDDY.NS', 'INDUSINDBK.NS', 'EICHERMOT.NS',
    'HEROMOTOCO.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'UPL.NS', 'BRITANNIA.NS',
    'SHREECEM.NS', 'APOLLOHOSP.NS', 'M&M.NS', 'SBICARD.NS', 'ADANIPORTS.NS'
]

def is_hammer(row):
    body = abs(row['Close'] - row['Open'])
    lower_shadow = min(row['Open'], row['Close']) - row['Low']
    upper_shadow = row['High'] - max(row['Open'], row['Close'])
    return lower_shadow > 2 * body and upper_shadow < body

def is_shooting_star(row):
    body = abs(row['Close'] - row['Open'])
    upper_shadow = row['High'] - max(row['Close'], row['Open'])
    lower_shadow = min(row['Close'], row['Open']) - row['Low']
    return upper_shadow > 2 * body and lower_shadow < body

shooting_star_hits = []
hammer_hits = []

for symbol in nifty50_symbols:
    print(f"🔍 Scanning {symbol}...")
    try:
        data = yf.download(tickers=symbol, interval='15m', period='5d', progress=False)

        if data.empty:
            print(f"⚠️ No data for {symbol} — possibly market closed.")
            continue

        data.dropna(inplace=True)
        data['is_hammer'] = data.apply(is_hammer, axis=1)
        data['is_shooting_star'] = data.apply(is_shooting_star, axis=1)

        data['date'] = data.index.date
        last_date = data['date'].max()
        last_day_data = data[data['date'] == last_date]

        if last_day_data.empty:
            continue

        latest = last_day_data.iloc[-1]
        day_high = last_day_data['High'].max()
        day_low = last_day_data['Low'].min()

        if latest['is_shooting_star'] and latest['High'] == day_high:
            shooting_star_hits.append(symbol)

        if latest['is_hammer'] and latest['Low'] == day_low:
            hammer_hits.append(symbol)

    except Exception as e:
        print(f"❌ Error with {symbol}: {e}")

message = "📈 <b>Pattern Scanner Results</b>\n"
message += "🔻 <b>Shooting Star at Day High</b>:\n" + "\n".join(shooting_star_hits or ["None"]) + "\n\n"
message += "🔻 <b>Hammer at Day Low</b>:\n" + "\n".join(hammer_hits or ["None"])
print(message)
send_telegram_alert(message)

