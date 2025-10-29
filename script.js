// 🌐 وظيفة التبديل بين اللغتين
document.querySelectorAll("#lang-switch button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const lang = btn.dataset.lang;
    document.querySelectorAll("[data-ar]").forEach((el) => {
      el.innerText = el.getAttribute(`data-${lang}`);
      document.documentElement.lang = lang;
      document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    });
  });
});
