# Telegram buyurtma bot (Python, kutubxonasiz)

Kafe, do'kon yoki xizmat uchun oddiy buyurtma bot: menyu → savat → ism, telefon, manzil → buyurtma bazaga yoziladi va sizga (adminga) keladi.

## Kerak bo'ladi
- Python 3.9 yoki yangi (python.org dan o'rnating)
- Hech qanday qo'shimcha kutubxona kerak emas

## Ishga tushirish
1. Telegram'da @BotFather → /newbot → bot yarating va **token** oling.
2. @userinfobot ga yozib, o'zingizning **ID** raqamingizni bilib oling.
3. `bot.py` ichida `PRODUCTS` ro'yxatini o'z mahsulotlaringizga almashtiring.
4. Terminalda (Windows: PowerShell):
   - Windows: `set BOT_TOKEN=token` va `set ADMIN_ID=123456`, keyin `python bot.py`
   - Mac/Linux: `BOT_TOKEN=token ADMIN_ID=123456 python3 bot.py`
5. Botga /start yozing.

## Sinab ko'rish (internetsiz)
`python test_bot.py` → "TEST OK" chiqsa, hammasi ishlaydi.

## Buyurtmalar qayerda?
`orders.db` faylida (SQLite). DB Browser for SQLite dasturi bilan ochsangiz bo'ladi.

## Doim ishlab turishi uchun
Kompyuter o'chsa bot ham to'xtaydi. 24/7 uchun arzon VPS yoki PythonAnywhere, Railway kabi xizmatlarga joylang.
