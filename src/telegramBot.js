import TelegramBot from "node-telegram-bot-api";
import { config } from "./config.js";
import { t } from "./i18n.js";
import { syncRepo } from "./commands/syncRepo.js";
import { deploy } from "./commands/deploy.js";

/**
 * 🤖 Telegram Bot Integration
 * دمج نواة ديف بوت مع تيليجرام
 */
const bot = new TelegramBot(config.TELEGRAM_TOKEN, { polling: true });

bot.onText(/\/start/, (msg) => bot.sendMessage(msg.chat.id, t(config.DEFAULT_LANG, "start")));
bot.onText(/\/help/, (msg) => bot.sendMessage(msg.chat.id, t(config.DEFAULT_LANG, "help")));
bot.onText(/\/sync/, async (msg) => {
  const repos = await syncRepo(config.DEFAULT_LANG);
  bot.sendMessage(msg.chat.id, `🔁 ${repos.join("\n")}`);
});
bot.onText(/\/deploy/, (msg) => deploy(config.DEFAULT_LANG));

console.log("🚀 Nawah DevBot Telegram integration is running...");
