import TelegramBot from "node-telegram-bot-api";
import dotenv from "dotenv";
dotenv.config();

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID;
const bot = new TelegramBot(token);

export async function sendNotification(message) {
  console.log("📣 Sending Telegram notification...");
  try {
    await bot.sendMessage(chatId, message);
  } catch (err) {
    console.error("⚠️ Failed to send Telegram message:", err);
  }
}
