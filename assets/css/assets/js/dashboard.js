// مثال: عرض آخر الأحداث من ملف logs/devbot.log
fetch('/logs/devbot.log')
  .then(res => res.text())
  .then(data => {
    const pre = document.createElement('pre');
    pre.textContent = data;
    document.body.appendChild(pre);
  })
  .catch(err => console.error('فشل تحميل سجل الأحداث:', err));
