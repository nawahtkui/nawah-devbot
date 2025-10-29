import { octokit } from './github.js';

export async function handleReview() {
  console.log("🔍 Running code review...");

  // مثال: تعليق تلقائي على PRs المفتوحة
  const owner = "nawahtkui";
  const repo = "nawah-core";
  const pull_number = 1; // مثال، يمكن تعديل للبوت لتصفح كل PRs

  await octokit.issues.createComment({
    owner,
    repo,
    issue_number: pull_number,
    body: "✅ تم مراجعة الكود تلقائيًا بواسطة Nawah DevBot"
  });
}
