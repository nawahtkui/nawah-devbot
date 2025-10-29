# 🧠 أمثلة عملية / Usage Examples

## 🇸🇦 بالعربية
تشغيل أمر التحقق من العقود الذكية:
```bash
nawah-devbot check-contract ./contracts/NawahToken.sol

مزامنة مستودع:
nawah-devbot sync --repo nawah-core

English 

Run smart contract verification

nawah-devbot check-contract ./contracts/NawahToken.sol

Sync repository:
nawah-devbot sync --repo nawah-core

---

### 5. `docs/api-reference.md`
```markdown
# 📘 واجهة البرمجة / API Reference

## 🇸🇦 بالعربية
| نقطة النهاية | الوصف | الطريقة |
|---------------|--------|----------|
| `/api/repos` | إرجاع قائمة المستودعات | GET |
| `/api/contracts/verify` | التحقق من العقود الذكية | POST |
| `/api/deploy` | نشر الإصدار الأخير | POST |

## 🇬🇧 English
| Endpoint | Description | Method |
|-----------|--------------|---------|
| `/api/repos` | Returns list of repositories | GET |
| `/api/contracts/verify` | Verifies smart contracts | POST |
| `/api/deploy` | Deploys latest version | POST |
