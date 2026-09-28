import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8757949960:AAHGclRKNpJvhplMWwrZg_r1PVJCEDuuyPs"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_formatted_ticker(symbol: str) -> str:
    symbol = symbol.upper().strip()
    
    if symbol.endswith(".IS") or symbol.endswith("-USD"):
        return symbol
        
    cryptos = ["BTC", "ETH", "SOL", "XRP", "ADA", "AVAX", "DOGE", "DOT", "LINK", "LTC", "SHIB", "PEPE"]
    if symbol in cryptos:
        return f"{symbol}-USD"
    
    # BİST Hisseleri içinVarsayılan .IS takısı
    return f"{symbol}.IS"

def get_crypto_binance(symbol: str):
    """Kripto paralar için Binance API üzerinden doğrudan veri çeker."""
    try:
        clean_symbol = symbol.replace("-USD", "").replace(".IS", "")
        url = f"https://api.binance.com/api/v3/klines?symbol={clean_symbol}USDT&interval=1d&limit=3"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if isinstance(data, list) and len(data) >= 2:
            prev_day = data[-2]
            high = float(prev_day[2])
            low = float(prev_day[3])
            close = float(prev_day[4])
            last_price = float(data[-1][4])
            return high, low, close, last_price
    except Exception as e:
        logging.error(f"Binance API Hata: {e}")
    return None

def get_stock_yahoo(symbol: str):
    """BİST ve NASDAQ için Yahoo Finance API üzerinden veri çeker."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        result = data['chart']['result'][0]
        quote = result['indicators']['quote'][0]
        
        highs = [h for h in quote['high'] if h is not None]
        lows = [l for l in quote['low'] if l is not None]
        closes = [c for c in quote['close'] if c is not None]
        
        if len(closes) >= 2:
            high = highs[-2]
            low = lows[-2]
            close = closes[-2]
            last_price = closes[-1]
            return high, low, close, last_price
    except Exception as e:
        logging.error(f"Yahoo API Hata: {e}")
    return None

def calculate_pivot_levels(ticker_symbol: str):
    formatted_ticker = get_formatted_ticker(ticker_symbol)
    data = None
    
    # Eğer kripto ise öncelikle Binance API dene
    if "-USD" in formatted_ticker:
        data = get_crypto_binance(formatted_ticker)
        
    # Kripto değilse veya Binance başarısızsa Yahoo API dene
    if not data:
        data = get_stock_yahoo(formatted_ticker)
        
    if not data:
        return f"❌ *{formatted_ticker}* sembolü bulunamadı veya veri alınamadı.\n💡 *Örnekler:* `ASELS`, `THYAO`, `BTC`, `AAPL`"
        
    high, low, close, last_price = data
    
    # Standart Pivot Seviyeleri
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    
    return (
        f"📊 *{formatted_ticker} Teknik Analiz*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💵 *Son Fiyat:* `{last_price:.2f}`\n\n"
        f"🔴 *Direnç 2 (R2):* `{r2:.2f}`\n"
        f"🔴 *Direnç 1 (R1):* `{r1:.2f}`\n"
        f"🎯 *Pivot Noktası:* `{pivot:.2f}`\n"
        f"🟢 *Destek 1 (S1):* `{s1:.2f}`\n"
        f"🟢 *Destek 2 (S2):* `{s2:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Kullanım:* BİST için `ASELS`, NASDAQ için `AAPL`, Kripto için `BTC` yazabilirsiniz."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Borsa & Kripto Destek/Direnç Botuna Hoş Geldiniz!*\n\n"
        "Analiz etmek istediğiniz sembolü yazıp gönderebilirsiniz.\n\n"
        "Örnekler:\n"
        "• BİST: `ASELS`, `ASTOR`, `THYAO`\n"
        "• Kripto: `BTC`, `ETH`, `SOL`\n"
        "• NASDAQ: `AAPL`, `TSLA`",
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
    
