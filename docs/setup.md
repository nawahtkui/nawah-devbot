# ⚙️ الإعداد / Setup

## 🇸🇦 بالعربية
### المتطلبات
- Node.js (الإصدار 18 أو أعلى)
- حساب GitHub مع صلاحيات إنشاء مستودعات
- مفتاح API خاص من OpenAI (اختياري)

### خطوات التشغيل
```bash
git clone https://github.com/nawahtkui/nawah-devbot.git
cd nawah-devbot
npm install
npm run dev
Requirements

Node.js v18+

A GitHub account with repo access

Optional: OpenAI API key

git clone https://github.com/nawahtkui/nawah-devbot.git
cd nawah-devbot
npm install
npm run dev


---

### 3. `docs/configuration.md`
```markdown
# ⚙️ إعدادات التكوين / Configuration

## 🇸🇦 بالعربية
ملف التكوين الرئيسي يوجد في:

src/config.js

يتضمن:
- `GITHUB_TOKEN`: مفتاح الوصول إلى GitHub.
- `OPENAI_KEY`: مفتاح واجهة الذكاء الاصطناعي.
- `DEFAULT_LANG`: اللغة الافتراضية (ar أو en).

## 🇬🇧 English
The main configuration file is located at:

src/config.js

Includes:
- `GITHUB_TOKEN`: Access token for GitHub.
- `OPENAI_KEY`: API key for AI integration.
- `DEFAULT_LANG`: Default language (ar or en).

