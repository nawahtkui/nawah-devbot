import { handleReview } from './review.js';
import { autoMerge } from './autoMerge.js';
import { createRelease } from './releaseManager.js';
import { sendNotification } from './notifier.js';

async function runBot() {
  console.log("🤖 Nawah DevBot started...");

  await handleReview();
  await autoMerge();
  await createRelease();
  await sendNotification("Nawah DevBot: عملية تلقائية اكتملت ✅");
}

runBot();
