import { octokit } from './github.js';
import fs from 'fs';
import { repositories } from '../config/repositories.json';

export async function createRelease() {
  console.log("🏷️ Creating releases...");

  for (const repoFull of repositories) {
    const [owner, repo] = repoFull.split("/");

    const tag_name = `v1.0.${Math.floor(Math.random() * 100)}`;
    const release = await octokit.repos.createRelease({
      owner,
      repo,
      tag_name,
      name: `Release ${tag_name}`,
      body: "🚀 إصدار تلقائي من Nawah DevBot"
    });

    logEvent(`Release ${tag_name} created in ${repoFull}`);
  }
}

function logEvent(message) {
  const log = `[${new Date().toISOString()}] ${message}\n`;
  fs.appendFileSync("logs/devbot.log", log);
}
