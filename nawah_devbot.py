
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os

TOKEN = os.getenv("TELEGRAM_TOKEN", "<YOUR_TELEGRAM_TOKEN>")

messages = {
    "start": {
        "ar": "مرحبًا بك في *Nawah DevBot* 🌟\nيرجى اختيار لغتك للمتابعة:",
        "en": "Welcome to *Nawah DevBot* 🌟\nPlease choose your language to continue:"
    },
    "about": {
        "ar": "🔹 *نواة (NWTK)* هي عملة رقمية تجمع بين التكنولوجيا والثقافة والتمكين.\n"
              "🔹 الهدف: دعم الإبداع، المرأة، والشباب.\n\nلنبدأ تسجيل بياناتك:",
        "en": "🔹 *Nawah (NWTK)* is a digital token uniting technology, culture, and empowerment.\n"
              "🔹 Goal: support creativity, women, and youth.\n\nLet's start registering your information:"
    },
    "ask_name": {"ar": "أرسل اسمك الكامل:", "en": "Please enter your full name:"},
    "ask_wallet": {"ar": "أرسل عنوان محفظتك:", "en": "Please enter your wallet address:"},
    "ask_country": {"ar": "أرسل دولتك:", "en": "Please enter your country:"},
    "kyc_done": {"ar": "✅ تم تسجيلك بنجاح!", "en": "✅ Registration completed successfully!"}
}

DATA_FILE = "./data/users.json"
os.makedirs("./data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

user_state = {}

def save_user(chat_id, user_data):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
    users[str(chat_id)] = user_data
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(messages["start"]["en"], reply_markup=reply_markup, parse_mode="Markdown")

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    chat_id = query.message.chat.id
    user_state[chat_id] = {"lang": lang, "step": "name", "data": {}}
    await query.edit_message_text(text=messages["about"][lang], parse_mode="Markdown")
    await query.message.reply_text(messages["ask_name"][lang])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = update.message.text
    state = user_state.get(chat_id)
    if not state:
        return
    lang = state["lang"]
    if state["step"] == "name":
        state["data"]["name"] = text
        state["step"] = "wallet"
        await update.message.reply_text(messages["ask_wallet"][lang])
    elif state["step"] == "wallet":
        state["data"]["wallet"] = text
        state["step"] = "country"
        await update.message.reply_text(messages["ask_country"][lang])
    elif state["step"] == "country":
        state["data"]["country"] = text
        save_user(chat_id, {**state["data"], "language": lang})
        del user_state[chat_id]
        await update.message.reply_text(messages["kyc_done"][lang])

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 Nawah DevBot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
