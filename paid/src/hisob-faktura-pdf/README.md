# Hisob-faktura (invoice) PDF generatori

`invoice.json` faylidagi ma'lumotdan chiroyli, jadvalli PDF hisob-faktura yasaydi: raqam, sana, sotuvchi/xaridor, mahsulotlar, jami, QQS, imzo joyi.

## O'rnatish
```
pip install reportlab
```

## Ishlatish
1. `invoice.json` ni o'z ma'lumotlaringiz bilan to'ldiring (Bloknot yoki VS Code'da).
2. `python invoice.py invoice.json hisob.pdf`

💡 QQS kerak bo'lmasa `"vat_percent": 0` qiling. Valyutani `"currency": "USD"` qilib o'zgartirsa bo'ladi.
⚠️ Bu oddiy tijorat hujjati namunasi. Rasmiy elektron hisob-faktura (soliq tizimi orqali) uchun soliq.uz/didox kabi tizimlardan foydalaning.
