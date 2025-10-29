import { exec } from "child_process";
import { t } from "../i18n.js";

/**
 * 🚀 Deploy latest version
 * نشر الإصدار الأخير تلقائيًا
 */
export function deploy(lang = "ar") {
  console.log("⚙️ Starting deployment...");
  exec("npm run build && npm run deploy", (err, stdout, stderr) => {
    if (err) {
      console.error(t(lang, "error"));
      return;
    }
    console.log("✅ Deployment complete!");
  });
}
