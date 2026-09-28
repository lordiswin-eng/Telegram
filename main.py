import logging
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8757949960:AAHGclRKNpJvhplMWwrZg_r1PVJCEDuuyPs"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_formatted_ticker(symbol: str) -> str:
    symbol = symbol.upper().strip()
    
    # Doğrudan girilen uzantılı semboller (.IS veya -USD)
    if symbol.endswith(".IS") or symbol.endswith("-USD"):
        return symbol
        
    # Kripto kontrolü
    cryptos = ["BTC", "ETH", "SOL", "XRP", "ADA", "AVAX", "DOGE", "DOT", "LINK", "LTC", "SHIB", "PEPE"]
    if symbol in cryptos:
        return f"{symbol}-USD"
    
    # BİST hisse varsayımı
    return f"{symbol}.IS"

def calculate_pivot_levels(ticker_symbol: str):
    formatted_ticker = get_formatted_ticker(ticker_symbol)
    
    try:
        ticker = yf.Ticker(formatted_ticker)
        data = ticker.history(period="5d", interval="1d")
        
        if data.empty or len(data) < 2:
            return f"❌ *{formatted_ticker}* sembolü bulunamadı veya veri alınamadı.\n💡 *İpucu:* BİST için hisse kodunu yazın (Örn: `ASELS`, `THYAO`)."
        
        # Son gün ve bir önceki gün verileri
        prev_day = data.iloc[-2]
        high = float(prev_day['High'])
        low = float(prev_day['Low'])
        close = float(prev_day['Close'])
        
        # Standart Pivot Hesaplamaları
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        last_price = float(data.iloc[-1]['Close'])
        
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
            f"💡 *Kullanım:* BİST için `ASELS`, `THYAO`, NASDAQ için `AAPL`, Kripto için `BTC` yazabilirsiniz."
        )
    except Exception as e:
        logging.error(f"Hata: {e}")
        return f"⚠️ Veri alınırken bir hata oluştu. Lütfen sembolü kontrol edin."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Borsa & Kripto Destek/Direnç Botuna Hoş Geldiniz!*\n\n"
        "Analiz etmek istediğiniz sembolü doğrudan mesaj olarak gönderebilirsiniz.\n\n"
        "Örnekler:\n"
        "• BİST: `ASELS`, `THYAO`, `GARAN`\n"
        "• Kripto: `BTC`, `ETH`, `SOL`\n"
        "• NASDAQ: `AAPL`, `TSLA`, `NVDA`",
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
    
