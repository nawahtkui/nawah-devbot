// ⚙️ إعدادات عامة
const GITHUB_API = "https://api.github.com/repos/nawahtkui/nawah-devbot";
const TELEGRAM_WEBHOOK = "https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/sendMessage";
const TELEGRAM_CHAT_ID = "<YOUR_CHAT_ID>"; // أضف رقم المحادثة الخاص بك

// 🟢 تحميل البيانات من GitHub API
async function loadDashboard() {
  try {
    // 🔹 حالة المستودع
    const repoData = await fetch(GITHUB_API).then(r => r.json());
    document.getElementById("repo-status").innerHTML = `
      📦 <b>${repoData.name}</b><br>
      🌿 الفرع الرئيسي: ${repoData.default_branch}<br>
      ⭐ النجوم: ${repoData.stargazers_count}<br>
      🕒 آخر تحديث: ${new Date(repoData.updated_at).toLocaleString()}
    `;

    // 🔹 آخر إصدار
    const releaseData = await fetch(`${GITHUB_API}/releases/latest`).then(r => r.json());
    document.getElementById("latest-release").innerHTML = `
      <b>${releaseData.name || "لا يوجد إصدار بعد"}</b><br>
      📅 ${new Date(releaseData.created_at).toLocaleDateString()}<br>
      🔗 <a href="${releaseData.html_url}" target="_blank">عرض في GitHub</a>
    `;

    // 🔹 آخر دمج (Pull Request)
    const pulls = await fetch(`${GITHUB_API}/pulls?state=closed`).then(r => r.json());
    const lastMerged = pulls.find(p => p.merged_at);
    if (lastMerged) {
      document.getElementById("last-merge").innerHTML = `
        #${lastMerged.number} - ${lastMerged.title}<br>
        🧑‍💻 ${lastMerged.user.login}<br>
        📅 ${new Date(lastMerged.merged_at).toLocaleDateString()}
      `;
    } else {
      document.getElementById("last-merge").innerText = "لا توجد عمليات دمج حديثة.";
    }

  } catch (err) {
    console.error(err);
    document.getElementById("repo-status").innerText = "⚠️ حدث خطأ أثناء جلب البيانات.";
  }
}

// 📩 إرسال إشعار إلى تيليجرام
async function sendTelegramNotification() {
  const text = "🚀 إشعار من Nawah DevBot: تم تنفيذ اختبار الإرسال بنجاح!";
  const url = `${TELEGRAM_WEBHOOK}?chat_id=${TELEGRAM_CHAT_ID}&text=${encodeURIComponent(text)}`;
  const result = document.getElementById("notify-result");

  try {
    const res = await fetch(url);
    if (res.ok) {
      result.innerText = "✅ تم إرسال الإشعار إلى تيليجرام بنجاح.";
    } else {
      result.innerText = "⚠️ فشل الإرسال، تحقق من التوكن أو رقم المحادثة.";
    }
  } catch (err) {
    result.innerText = "❌ خطأ في الاتصال بالخادم.";
  }
}

// 📌 الأحداث
document.addEventListener("DOMContentLoaded", loadDashboard);
document.getElementById("send-notify").addEventListener("click", sendTelegramNotification);
