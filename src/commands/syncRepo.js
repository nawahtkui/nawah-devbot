import { Octokit } from "@octokit/rest";
import { config } from "../config.js";
import { t } from "../i18n.js";

/**
 * 🔁 Sync GitHub repository
 * مزامنة مستودع جيثب
 */
export async function syncRepo(lang = "ar") {
  try {
    const octokit = new Octokit({ auth: config.GITHUB_TOKEN });
    const repos = await octokit.repos.listForUser({ username: config.REPO_OWNER });
    console.log(t(lang, "status"));
    return repos.data.map((r) => r.name);
  } catch (error) {
    console.error(error);
    return t(lang, "error");
  }
}
