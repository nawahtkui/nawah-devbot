import express from "express";
import { config } from "./config.js";
import { t } from "./i18n.js";

const app = express();

app.get("/", (req, res) => {
  res.send(`<h2>${config.BOT_NAME}</h2><p>${t("ar", "start")}</p>`);
});

app.listen(3000, () => {
  console.log(`✅ ${config.BOT_NAME} running at http://localhost:3000`);
});
