import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
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

    await query.message.reply_text(
        "โอนเงิน 199 บาท ผ่าน PromptPay\nเมื่อโอนแล้ว กดปุ่มด้านล่างเพื่อแจ้งโอน"
    )

    keyboard = [[InlineKeyboardButton("แจ้งโอนแล้ว", callback_data="confirm")]]
    await query.message.reply_text(
        "กดปุ่มเพื่อยืนยัน",
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

    requests.post(WEBHOOK_URL, json=payload, timeout=10)

    await query.message.reply_text(
        "รับแจ้งโอนแล้ว ✅\nแอดมินจะตรวจสอบและเชิญเข้ากลุ่ม VIP"
    )

if __name__ == "__main__":
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_vip, pattern="buy_vip"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="confirm"))

    app.run_polling()

