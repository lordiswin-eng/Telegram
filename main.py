import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8757949960:AAHGclRKNpJvhplMWwrZg_r1PVJCEDuuyPs"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Yaygın kripto isimlerinin Borsa Kodları eşleştirmesi
CRYPTO_MAP = {
    "TRON": "TRX",
    "BITCOIN": "BTC",
    "ETHEREUM": "ETH",
    "RIPPLE": "XRP",
    "DOGECOIN": "DOGE"
}

def get_crypto_binance(symbol: str):
    """Binance API üzerinden Pivot verilerini çeker."""
    try:
        clean_symbol = symbol.upper().strip()
        clean_symbol = CRYPTO_MAP.get(clean_symbol, clean_symbol).replace("-USD", "").replace(".IS", "")
        
        url = f"https://api.binance.com/api/v3/klines?symbol={clean_symbol}USDT&interval=1d&limit=3"
        res = requests.get(url, timeout=5)
        data = res.json()
        
        if isinstance(data, list) and len(data) >= 2:
            prev_day = data[-2]
            high = float(prev_day[2])
            low = float(prev_day[3])
            close = float(prev_day[4])
            last_price = float(data[-1][4])
            return high, low, close, last_price, f"{clean_symbol}-USD"
    except Exception as e:
        logging.error(f"Binance Hata: {e}")
    return None

def get_stock_stooq(symbol: str):
    """Stooq API üzerinden BİST/NASDAQ verilerini çeker."""
    try:
        clean_symbol = symbol.upper().replace(".IS", "").replace("-USD", "").strip()
        formatted = f"{clean_symbol}.TR"
        
        url = f"https://stooq.com/q/l/?s={formatted}&f=sdohcv&h&e=csv"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=5)
        
        lines = res.text.strip().split('\n')
        if len(lines) >= 2:
            row = lines[1].split(',')
            if len(row) >= 6 and row[1] != 'N/A':
                high = float(row[3])
                low = float(row[4])
                close = float(row[5])
                return high, low, close, close, f"{clean_symbol}.IS"
    except Exception as e:
        logging.error(f"Stooq Hata: {e}")
    return None

def calculate_pivot_levels(symbol: str):
    # 1. Kripto olarak dene
    data = get_crypto_binance(symbol)
    
    # 2. Kripto değilse BİST/Hisse olarak dene
    if not data:
        data = get_stock_stooq(symbol)
        
    if not data:
        return f"❌ *{symbol.upper()}* sembolü bulunamadı.\n💡 *Örnekler:* `THYAO`, `ASELS`, `ASTOR`, `BTC`, `TRX`"
        
    high, low, close, last_price, ticker_name = data
    
    # Standart Pivot Seviyeleri
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
