import json
V=json.load(open('cfg.json')); V=[v for v in V if v['id'][0] not in 'pe']
RULES=[["🗓","Botga kirgandan 15 kun keyin yechasiz"],["💸","Keyin istalgan vaqtda, 50 000 so'mdan"],["⚠️","Kafolat yo'q: faqat tasdiqlangan to'lov"]]
CAP=("{h}\n\n🔥 AKSIYA: 4-dekabrgacha har bir tasdiqlangan do'st uchun 20 000 so'm bonus.\n\nQanday ishlaydi:\n"
 "1) Telegram'da @A1Prompt_bot'ga kiring (profildagi havola), «Referal havolam» tugmasidan shaxsiy havola oling.\n"
 "2) Havolani AI'ga qiziqadigan do'stlaringizga yuboring.\n3) Do'stingiz yopiq kanalga to'lov qilsa va to'lovi tasdiqlansa, balansingizga 20 000 so'm yoziladi.\n\n"
 "Shartlar:\n🗓 Botga kirganingizdan 15 kun o'tgach yechish ochiladi.\n💸 Keyin istalgan vaqtda kartaga yechasiz, kamida 50 000 so'm.\n"
 "✅ Yopiq kanalni sotib olmagan bo'lsangiz ham qatnashasiz.\n⚠️ Daromad kafolatlanmaydi: bonus faqat tasdiqlangan to'lovdan yoziladi.\n"
 "4-dekabrdan keyin bonus 10 000 so'm bo'ladi.\n\nYopiq kanalda: har kuni yangi promptlar, n8n shablon fayllari, ilovalar va kod loyihalari (100 000 so'm, bir martalik).\n"
 "🆓 Bepul namunalar: t.me/AIPromptMasters\n\n📤 Bu videoni AI'ga qiziqadigan do'stlaringizga yuboring.\n\n#aksiya #bonus #telegram #ai #uzbekistan")
def mk(id,accent,a2,pill,hook,steps,calc,end1,enote):
    return dict(id=id,fmt='C',accent=accent,accent2=a2,pill=pill,hook=hook,steps=steps,calcTitle="Hisob <hl>oddiy:</hl>",calc=calc,rules=RULES,
      H=2.2,calcAt=5.6,E=11.2,T=14.2,end1=end1,chips=["👥 Referal havola","💰 Balans botda","💸 Kartaga yechish"],enote=enote,
      caption=CAP.format(h=hook.replace('<hl>','').replace('</hl>','')))
S1=[["Botdan havola oling","«Referal havolam» tugmasi"],["Do'stingizga yuboring","U yopiq kanalga to'lov qiladi"],["Balansga +20 000 so'm","To'lovi tasdiqlangach yoziladi"]]
S2=[["Kanal sotib olish shart emas","Faqat botga kiring"],["Havolangizni ulashing","Do'stlar, guruhlar, oila"],["Har bir to'lov = +20 000 so'm","4-dekabrgacha amal qiladi"]]
C3=[["1 do'st","20 000 so'm"],["3 do'st","60 000 so'm"],["10 do'st","200 000 so'm"]]
C5=[["3 do'st","60 000 so'm"],["5 do'st","100 000 so'm"],["10 do'st","200 000 so'm"]]
END="Aksiya <hl>4-dekabrgacha</hl>. Havolani botdan oling"
P=[mk('p00','#FF9F43','#FF3D71','🔥 AKSIYA 4-DEKABRGACHA',"Do'stingiz obuna bo'lsa, sizga <hl>20 000 so'm</hl>",S1,C3,END,"📤 Videoni do'stlaringizga yuboring"),
   mk('p01','#FF9F43','#FF3D71','🔥 AKSIYA 4-DEKABRGACHA',"10 ta do'st = <hl>200 000 so'm</hl>. Shartlari 👇",S2,C5,END,"📤 Videoni do'stlaringizga yuboring")]
H=["Bonus <hl>2 baravar</hl> oshdi: endi 20 000 so'm","Kanalga kirmasdan ham <hl>bonus</hl> yig'sa bo'ladi","Havolani ulashing, <hl>20 000 so'm</hl> oling 👇",
   "5 do'st = <hl>100 000 so'm</hl>. Qanday ishlaydi?","Aksiya shartlari: <hl>halol</hl> va aniq 👇","Do'stlaringiz AI'ga qiziqadimi? <hl>Havolangizni</hl> ulashing"]
for i,h in enumerate(H):
    P.append(mk(f'e{i:02d}','#3DDC84','#00B3FF','🔥 AKSIYA 4-DEKABRGACHA',h,S2 if i in (1,4) else S1,C5 if i in (3,) else C3,END,"⚠️ Daromad kafolatlanmaydi"))
V+=P; json.dump(V,open('cfg.json','w'),ensure_ascii=False,indent=1)
for p in P: assert len(p['caption'])<2100
print([p['id'] for p in P])
