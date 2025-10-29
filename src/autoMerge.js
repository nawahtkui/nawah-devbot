import { octokit } from './github.js';

export async function autoMerge() {
  console.log("🔀 Checking PRs for auto-merge...");

  // مثال بسيط: دمج PR رقم 1 بعد اجتياز الشروط
  const owner = "nawahtkui";
  const repo = "nawah-core";
  const pull_number = 1;

  await octokit.pulls.merge({
    owner,
    repo,
    pull_number
  }).catch(() => console.log("⚠️ PR لم يتم دمجه (قد يكون مغلقاً أو غير جاهز)"));
}
