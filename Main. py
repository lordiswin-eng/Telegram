import logging
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token'ınız koda eklenmiştir
TOKEN = "8757949960:AAHGclRKNpJvhplMWwrZg_r1PVJCEDuuyPs"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_formatted_ticker(symbol: str) -> str:
    symbol = symbol.upper().strip()
    # Popüler Kripto paralar için USD çifti
    if symbol in ["BTC", "ETH", "SOL", "XRP", "ADA", "AVAX", "DOGE"]:
        return f"{symbol}-USD"
    # BİST / NASDAQ ayrımı (.IS ekleme)
    if not symbol.endswith(".IS") and not symbol.endswith("-USD"):
        if len(symbol) <= 5:
            return f"{symbol}.IS"
    return symbol

def calculate_pivot_levels(ticker_symbol: str):
    formatted_ticker = get_formatted_ticker(ticker_symbol)
    try:
        data = yf.download(formatted_ticker, period="5d", interval="1d", progress=False)
        if data.empty or len(data) < 2:
            return f"❌ *{ticker_symbol}* sembolü bulunamadı veya veri alınamadı."
        
        prev_day = data.iloc[-2]
        high = float(prev_day['High'])
        low = float(prev_day['Low'])
        close = float(prev_day['Close'])
        
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
        )
    except Exception as e:
        return f"⚠️ Veri alınırken hata oluştu."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Borsa & Kripto Destek/Direnç Botuna Hoş Geldiniz!\n\nAnaliz etmek istediğiniz sembolü yazabilirsiniz.\nÖrnek: `THYAO`, `AAPL` veya `BTC`", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip()
    await update.message.reply_text("⏳ Veriler hesaplanıyor...")
    result = calculate_pivot_levels(symbol)
    await update.message.reply_text(result, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
