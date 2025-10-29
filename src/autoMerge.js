import { octokit } from './github.js';
import fs from 'fs';
import { repositories } from '../config/repositories.json';

export async function autoMerge() {
  console.log("🔀 Checking PRs for auto-merge...");

  for (const repoFull of repositories) {
    const [owner, repo] = repoFull.split("/");

    const { data: prs } = await octokit.pulls.list({ owner, repo, state: "open" });

    for (const pr of prs) {
      try {
        await octokit.pulls.merge({ owner, repo, pull_number: pr.number });
        logEvent(`PR #${pr.number} merged in ${repoFull}`);
      } catch {
        logEvent(`PR #${pr.number} could not be merged in ${repoFull}`);
      }
    }
  }
}

function logEvent(message) {
  const log = `[${new Date().toISOString()}] ${message}\n`;
  fs.appendFileSync("logs/devbot.log", log);
}
