import logging
import requests
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


TOKEN = "8757949960:AAHGclRKNpJvhplMWwrZg_r1PVJCEDuuyPs"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

CRYPTO_MAP = {
    "TRON": "TRX", "BITCOIN": "BTC", "ETHEREUM": "ETH", "RIPPLE": "XRP", "DOGECOIN": "DOGE"
}

def get_crypto_data(symbol: str):
    clean = symbol.upper().strip()
    clean = CRYPTO_MAP.get(clean, clean).replace("-USD", "").replace(".IS", "")
    
    # 1. Yöntem: Binance API
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={clean}USDT&interval=1d&limit=3"
        res = requests.get(url, timeout=5)
        data = res.json()
        if isinstance(data, list) and len(data) >= 2:
            prev_day = data[-2]
            return float(prev_day[2]), float(prev_day[3]), float(prev_day[4]), float(data[-1][4]), f"{clean}-USD"
    except Exception as e:
        logging.error(f"Binance API Hata: {e}")

    # 2. Yöntem: Yahoo Finance (Yedek Kripto)
    try:
        ticker = yf.Ticker(f"{clean}-USD")
        df = ticker.history(period="5d")
        if len(df) >= 2:
            prev_day = df.iloc[-2]
            last_day = df.iloc[-1]
            return float(prev_day['High']), float(prev_day['Low']), float(prev_day['Close']), float(last_day['Close']), f"{clean}-USD"
    except Exception as e:
        logging.error(f"Yahoo Crypto Hata: {e}")
        
    return None

def get_bist_data(symbol: str):
    clean = symbol.upper().replace(".IS", "").replace("-USD", "").strip()
    
    # Yahoo Finance (BİST Hisseleri)
    try:
        ticker = yf.Ticker(f"{clean}.IS")
        df = ticker.history(period="5d")
        if len(df) >= 2:
            prev_day = df.iloc[-2]
            last_day = df.iloc[-1]
            return float(prev_day['High']), float(prev_day['Low']), float(prev_day['Close']), float(last_day['Close']), f"{clean}.IS"
    except Exception as e:
        logging.error(f"Yahoo BIST Hata: {e}")

    return None

def calculate_pivot_levels(symbol: str):
    data = get_crypto_data(symbol)
    if not data:
        data = get_bist_data(symbol)
        
    if not data:
        return f"❌ *{symbol.upper()}* sembolü bulunamadı veya verisine ulaşılamadı.\n💡 *Örnekler:* `THYAO`, `ASELS`, `ASTOR`, `BTC`, `TRX`"
        
    high, low, close, last_price, ticker_name = data
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    
    return (
        f"📊 *{ticker_name} Teknik Analiz*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💵 *Son Fiyat:* `{last_price:.2f}`\n\n"
        f"🔴 *Direnç 2 (R2):* `{r2:.2f}`\n"
        f"🔴 *Direnç 1 (R1):* `{r1:.2f}`\n"
        f"🎯 *Pivot Noktası:* `{pivot:.2f}`\n"
        f"🟢 *Destek 1 (S1):* `{s1:.2f}`\n"
        f"🟢 *Destek 2 (S2):* `{s2:.2f}`\n"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Borsa & Kripto Destek/Direnç Botuna Hoş Geldiniz!*\n\n"
        "Analiz etmek istediğiniz sembolü yazın:\n"
        "• BİST: `ASELS`, `ASTOR`, `THYAO`\n"
        "• Kripto: `BTC`, `TRX`, `ETH`",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip()
    await update.message.reply_text("⏳ Veriler hesaplanıyor...")
    result = calculate_pivot_levels(symbol)
    await update.message.reply_text(result, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)
        
