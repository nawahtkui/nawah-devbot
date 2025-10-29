import { octokit } from './github.js';

export async function createRelease() {
  console.log("🏷️ Creating release...");

  const owner = "nawahtkui";
  const repo = "nawah-core";
  const tag_name = `v1.0.${Math.floor(Math.random()*100)}`; // مثال بسيط

  await octokit.repos.createRelease({
    owner,
    repo,
    tag_name,
    name: `Release ${tag_name}`,
    body: "🚀 إصدار تلقائي من Nawah DevBot"
  });
}
