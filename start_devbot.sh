#!/bin/bash
# ===============================
# Nawah DevBot Auto Setup & Run (Enhanced)
# ===============================

REPO_DIR=~/downloads/nawah-devbot
BRANCH=devbot-kyc
SSH_KEY=~/.ssh/id_ed25519_nawahtoken
TOKEN_FILE=.env

# -------------------------------
# 1️⃣ الانتقال إلى مجلد المستودع
# -------------------------------
mkdir -p $REPO_DIR
cd $REPO_DIR || exit

# -------------------------------
# 2️⃣ تشغيل وكيل SSH وإضافة المفتاح
# -------------------------------
eval $(ssh-agent)
ssh-add $SSH_KEY

# -------------------------------
# 3️⃣ استنساخ المستودع أو تحديثه
# -------------------------------
if [ ! -d .git ]; then
    git clone git@github.com:nawahtkui/nawah-devbot.git .
fi

git fetch origin
git checkout $BRANCH || git checkout -b $BRANCH
git pull origin $BRANCH

# -------------------------------
# 4️⃣ إعداد GitHub SSH Remote
# -------------------------------
git remote set-url origin git@github.com:nawahtkui/nawah-devbot.git

# -------------------------------
# 5️⃣ دفع أي تغييرات تلقائيًا
# -------------------------------
git add .
git commit -m "Auto-commit from start_devbot.sh" 2>/dev/null
git push -u origin $BRANCH 2>/dev/null || echo "Push failed, تحقق من صلاحية المفتاح"

# -------------------------------
# 6️⃣ تثبيت المكتبات المطلوبة
# -------------------------------
pip install python-telegram-bot==20.6 --upgrade

# -------------------------------
# 7️⃣ إنشاء ملف .env للتوكن
# -------------------------------
if [ ! -f $TOKEN_FILE ]; then
    echo "TELEGRAM_TOKEN=123456789:ABCDefGHIjklMNO_pQrStuvWXyZ" > $TOKEN_FILE
fi

# -------------------------------
# 8️⃣ إعداد رسائل ثنائية اللغة + KYC
# -------------------------------
cat > messages.json <<EOL
{
    "en": {
        "welcome": "Welcome to Nawah DevBot!\\n- Empowering youth and women in digital economy.\\n- Explore USNT project features.\\n- Use /kyc to register.",
        "kyc_prompt": "Please enter your full name and ID for KYC verification:"
    },
    "ar": {
        "welcome": "مرحبًا بك في Nawah DevBot!\\n- تمكين الشباب والمرأة في الاقتصاد الرقمي.\\n- استكشف ميزات مشروع USNT.\\n- استخدم /kyc للتسجيل.",
        "kyc_prompt": "يرجى إدخال اسمك الكامل ورقم هويتك للتحقق:"
    }
}
EOL

# -------------------------------
# 9️⃣ تشغيل البوت مع دعم التحديث التلقائي
# -------------------------------
echo "🤖 تشغيل Nawah DevBot..."
while true; do
    python nawah_devbot.py
    echo "⚡ البوت توقف، إعادة التشغيل بعد 5 ثوانٍ..."
    sleep 5
    git pull origin $BRANCH
done

