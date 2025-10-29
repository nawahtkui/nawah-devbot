/**
 * 🌐 i18n (Internationalization)
 * نظام الترجمة للغتين: العربية والإنجليزية
 */

export const i18n = {
  ar: {
    start: "🤖 أهلاً بك في نواة ديف بوت! كيف يمكنني مساعدتك اليوم؟",
    help: "يمكنك استخدام الأوامر التالية:\n- /sync لمزامنة المستودع\n- /status لعرض الحالة\n- /deploy لنشر التحديث الأخير",
    status: "📊 حالة النظام: كل شيء يعمل بشكل طبيعي.",
    error: "❌ حدث خطأ أثناء التنفيذ، يرجى المحاولة لاحقًا.",
  },
  en: {
    start: "🤖 Welcome to Nawah DevBot! How can I help you today?",
    help: "You can use the following commands:\n- /sync to sync repository\n- /status to view system status\n- /deploy to deploy latest release",
    status: "📊 System status: Everything is running smoothly.",
    error: "❌ An error occurred while executing. Please try again later.",
  },
};

export function t(lang, key) {
  return i18n[lang]?.[key] || i18n.en[key] || key;
}
