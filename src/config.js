/**
 * 🔧 Nawah DevBot Configuration
 * إعدادات التكوين العامة للبوت
 */

export const config = {
  GITHUB_TOKEN: process.env.GITHUB_TOKEN || "YOUR_GITHUB_TOKEN_HERE",
  OPENAI_KEY: process.env.OPENAI_KEY || "YOUR_OPENAI_KEY_HERE",
  TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN || "",
  DEFAULT_LANG: process.env.DEFAULT_LANG || "ar", // ar أو en
  REPO_OWNER: "nawahtkui",
  BASE_URL: "https://nawahtkui.github.io/nawah-devbot",
  BOT_NAME: "Nawah DevBot",
};
