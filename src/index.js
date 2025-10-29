import { handleReview } from './review.js';
import { autoMerge } from './autoMerge.js';
import { createRelease } from './releaseManager.js';
import { sendNotification } from './notifier.js';

async function runBot() {
  console.log("🤖 Nawah DevBot started...");

  try {
    await handleReview();
    await autoMerge();
    await createRelease();
    await sendNotification("✅ Nawah DevBot: العملية التلقائية اكتملت بنجاح");
  } catch (err) {
    console.error("⚠️ خطأ أثناء تشغيل البوت:", err);
    await sendNotification(`⚠️ Nawah DevBot: حدث خطأ - ${err.message}`);
  }
}

runBot();
