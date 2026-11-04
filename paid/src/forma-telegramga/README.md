# Saytdagi ariza formasi → to'g'ridan-to'g'ri Telegramingizga

Mijoz saytda ism, telefon, izoh yozadi → sizga Telegram'da xabar keladi. Bot token sayt kodida ko'rinmaydi (xavfsiz), chunki xabar Cloudflare Worker orqali o'tadi. Cloudflare Worker bepul (kuniga 100 000 so'rovgacha).

## Sozlash (15 daqiqa)
1. @BotFather'da bot yarating, token oling. Botga /start yozing. @userinfobot'dan o'z ID'ingizni oling.
2. dash.cloudflare.com → ro'yxatdan o'ting → Workers & Pages → Create → Worker → "Hello World" → Deploy → Edit code.
3. `worker.js` ichidagi kodni to'liq qo'ying → Deploy.
4. Worker → Settings → Variables and Secrets: `BOT_TOKEN` (Secret), `CHAT_ID` (ID raqamingiz), `ALLOWED_ORIGIN` (saytingiz manzili yoki `*`).
5. `index.html` dagi `ENDPOINT` ga worker manzilini yozing (masalan `https://forma.ismingiz.workers.dev`).
6. `index.html` ni saytingizga qo'ying (yoki shu forma kodini mavjud sahifangizga ko'chiring).

## Nimalar bor
- Telefon raqamini tekshirish, spam botlardan himoya (yashirin maydon)
- Mobilga moslashgan dizayn
- Xabar: ism, telefon, xizmat turi, izoh
