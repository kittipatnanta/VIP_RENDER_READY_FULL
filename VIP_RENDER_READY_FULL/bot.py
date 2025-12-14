import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://vip-render-ready-full.onrender.com/payment/webhook"
PROMPTPAY_AMOUNT = 199

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("สมัคร VIP 199 บาท", callback_data="buy_vip")]]
    await update.message.reply_text(
        "สมัคร VIP เพื่อเข้าถึงคอนเทนต์พิเศษ",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("ยืนยันการชำระเงิน", callback_data="confirm")]]
    await query.message.reply_text(
        "โอนเงิน 199 บาท ผ่าน PromptPay แล้วกดยืนยัน",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    payload = {
        "post_id": 1,
        "user_id": query.from_user.id,
        "amount": PROMPTPAY_AMOUNT
    }

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
        await query.message.reply_text("✅ รับข้อมูลเรียบร้อย รอแอดมินตรวจสอบ")
    except Exception:
        await query.message.reply_text("❌ ระบบขัดข้อง กรุณาลองใหม่")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_vip, pattern="buy_vip"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="confirm"))

    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
