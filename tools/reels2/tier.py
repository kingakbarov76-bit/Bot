import json
V = json.load(open('cfg.json'))
V = [v for v in V if not v['id'].startswith('t')]
CAP = ("1000 ta xaridor olib keling: har biri uchun 40 000 so'm\n\n"
 "🏆 KATTA AKSIYA (4-dekabrgacha): agar siz bir o'zingiz 1000 va undan ko'p xaridor olib kelsangiz, har bir xaridor uchun 40 000 so'm olasiz. "
 "Avvalgi xaridorlaringiz ham 40 000 so'mdan qayta hisoblanadi.\n\n"
 "Misol:\n• 100 ta xaridor: 2 000 000 so'm (har biri 20 000)\n• 999 ta xaridor: 19 980 000 so'm\n• 1000 ta xaridor: 40 000 000 so'm (har biri 40 000)\n\n"
 "Kimlar uchun: Telegram kanal egalari, blogerlar, katta guruh adminlari.\n\n"
 "Qanday ishlaydi:\n1) Telegram'da @A1Prompt_bot'ga kiring (profildagi havola), «Referal havolam» tugmasidan shaxsiy havola oling.\n"
 "2) Havolani auditoriyangizga ulashing.\n3) Har bir tasdiqlangan to'lov balansingizga yoziladi. Botda «Balans» bo'limida hisoblagich bor: 0 / 1000.\n\n"
 "Shartlar:\n👥 1000 tagacha har bir xaridor uchun 20 000 so'm (hamma uchun aksiya).\n"
 "🗓 Botga kirganingizdan 15 kun o'tgach yechish ochiladi, keyin istalgan vaqtda, kamida 50 000 so'm.\n"
 "⏳ Hisob 4-noyabrdan 4-dekabr 23:59 gacha tasdiqlangan to'lovlar bo'yicha.\n"
 "⚠️ Daromad kafolatlanmaydi: bonus faqat haqiqiy, tasdiqlangan to'lovdan yoziladi.\n\n"
 "Yopiq kanalda: har kuni yangi promptlar, n8n shablon fayllari, ilovalar va kod loyihalari (100 000 so'm, bir martalik).\n"
 "🆓 Bepul namunalar: t.me/AIPromptMasters\n\n📤 Bu videoni kanal egasi yoki bloger do'stingizga yuboring.\n\n"
 "#aksiya #bonus #bloger #telegram #ai #uzbekistan")
T = dict(id='t00', fmt='C', accent='#FFC542', accent2='#FF7A00', pill='🏆 KATTA AKSIYA 4‑DEKABRGACHA',
  hook="1000 ta xaridor olib keling: har biri uchun <hl>40 000 so'm</hl>",
  steps=[["Botdan havola oling", "«Referal havolam» tugmasi"],
         ["Auditoriyangizga ulashing", "Kanal, guruh, blog"],
         ["1000+ xaridor: har biri 40 000", "Avvalgilari ham qayta hisoblanadi"]],
  calcTitle="Hisob <hl>oddiy:</hl>",
  calc=[["100 xaridor", "2 000 000 so'm"], ["999 xaridor", "19 980 000 so'm"], ["1000 xaridor", "40 000 000 so'm"]],
  rules=[["👥", "1000 tagacha: har biri 20 000 so'm"], ["🗓", "Botga kirgandan 15 kun keyin yechasiz"], ["⚠️", "Kafolat yo'q: faqat tasdiqlangan to'lov"]],
  H=2.2, calcAt=5.6, E=11.2, T=14.2,
  end1="Aksiya <hl>4-dekabrgacha</hl>. Havolani botdan oling",
  chips=["📣 Blogerlar uchun", "👥 Referal havola", "💸 Kartaga yechish"],
  enote="📤 Videoni bloger do'stingizga yuboring",
  caption=CAP)
assert len(CAP) < 2100, len(CAP)
V.append(T)
json.dump(V, open('cfg.json', 'w'), ensure_ascii=False, indent=1)
print('ok', len(CAP))
