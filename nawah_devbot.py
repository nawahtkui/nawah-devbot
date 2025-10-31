import os, json, sqlite3
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# تحميل التوكن وتهيئة قاعدة البيانات
load_dotenv(os.path.join('config', '.env') if os.path.exists(os.path.join('config', '.env')) else '.env')
TOKEN = os.getenv('TELEGRAM_TOKEN')
DB_PATH = os.getenv('DB_PATH', 'nawah_kyc.db')

# إنشاء جدول KYC إن لم يكن موجود
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kyc (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    national_id TEXT,
                    email TEXT,
                    timestamp_utc TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# تحميل الرسائل
with open("messages.json", "r", encoding="utf-8") as f:
    MESSAGES = json.load(f)

# حفظ بيانات KYC
def save_kyc(user_id, name, nid, email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO kyc (user_id, full_name, national_id, email, timestamp_utc) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, nid, email, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = "ar"
    await update.message.reply_text(MESSAGES[lang]["welcome"])

async def kyc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = "ar"
    await update.message.reply_text(MESSAGES[lang]["kyc_prompt"])

async def handle_kyc_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    parts = [p.strip() for p in update.message.text.split(",")]
    if len(parts) != 3:
        await update.message.reply_text(
            "❌ يرجى إدخال البيانات بالترتيب: الاسم الكامل، رقم الهوية، البريد الإلكتروني."
        )
        return
    full_name, national_id, email = parts
    save_kyc(user_id, full_name, national_id, email)
    await update.message.reply_text(
        f"✅ تم استلام بياناتك بنجاح:\nالاسم: {full_name}\nالهوية: {national_id}\nالإيميل: {email}"
    )

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kyc", kyc))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_kyc_input))
    print("🤖 Nawah DevBot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
