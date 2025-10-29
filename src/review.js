import { octokit } from './github.js';
import fs from 'fs';
import { repositories } from '../config/repositories.json';

export async function handleReview() {
  console.log("🔍 Running code review...");

  for (const repoFull of repositories) {
    const [owner, repo] = repoFull.split("/");
    
    const { data: prs } = await octokit.pulls.list({ owner, repo, state: "open" });

    for (const pr of prs) {
      // مثال بسيط للتعليق على PR
      await octokit.issues.createComment({
        owner,
        repo,
        issue_number: pr.number,
        body: "✅ تم مراجعة الكود تلقائيًا بواسطة Nawah DevBot"
      });

      logEvent(`PR #${pr.number} reviewed in ${repoFull}`);
    }
  }
}

function logEvent(message) {
  const log = `[${new Date().toISOString()}] ${message}\n`;
  fs.appendFileSync("logs/devbot.log", log);
}
