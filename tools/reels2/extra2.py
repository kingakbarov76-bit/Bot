import json
exec(open('extra.py').read().split("A=[")[0])  # FOOT, HOW, pl, CH
A=[
("Rasm uchun <hl>sotuvchi matn</hl> kerakmi? 👇","Sen kopirayter va marketologsan. [mahsulot] uchun infografika matni yoz. Xususiyatlari: [ro'yxat]. Xaridor muammosi: [muammo]. Format: 5-7 so'zli sarlavha, 3 ta qisqa foyda, chaqiriq. O'zbek tilida.",
 ["Rasm uchun sarlavha","3 ta qisqa foyda","Sotuvga chaqiriq"],90,"#infografika #marketplace #prompt #chatgpt #uzbekistan"),
("Mijoz bilan <hl>janjal</hl> chiqdimi? 👇","Sen nizolarni hal qilish mutaxassisisan. [mijoz va xodim] o'rtasida ziddiyat bor: [qisqacha holat]. Ikkala tomonni tinchlantiradigan muloqot usullari va aniq yechim takliflarini ber.",
 ["Tinch muloqot usullari","Aniq yechim takliflari","Mijozni saqlashga yordam"],93,"#mijoz #servis #prompt #chatgpt #uzbekistan"),
("Instagram reklama matnini <hl>AI yozsin</hl> 👇","Sen SMM kopirayterisan. [mahsulot] uchun Instagram reklama matni yoz. Auditoriya: [kim]. Muammo: [og'riq]. Yechim: [foyda]. Tuzilma: sarlavha, muammo, yechim, chaqiriq. Do'stona ohangda.",
 ["Tayyor reklama matni","Muammo → yechim tuzilmasi","Aniq chaqiriq"],109,"#reklama #instagram #prompt #chatgpt #uzbekistan"),
("Mijoz sharhlaridan <hl>foyda</hl> oling 👇","Sen marketing tahlilchisisan. Mana mijozlar sharhlari: [sharhlar]. Tahlil qil: eng yoqqan 3 narsa, takroriy shikoyatlar, mijozlar ishlatgan iboralar va biznesni yaxshilash uchun 3 ta qadam.",
 ["Yoqqan va yoqmagan narsalar","Mijozlar tili","3 ta aniq qadam"],113,"#biznes #tahlil #prompt #chatgpt #uzbekistan"),
("Yig'ilishdan keyin <hl>vazifalar ro'yxati</hl> 👇","Sen loyiha menejerisan. Mana yig'ilish matni: [matn]. 3-4 gapli xulosa va vazifalar ro'yxatini tuz: kim, nima, qachongacha. Noaniq joyni \"aniqlashtirilsin\" deb belgila.",
 ["Qisqa xulosa","Kim nima qiladi","Muddatlar bilan"],116,"#jamoa #boshqaruv #prompt #chatgpt #uzbekistan"),
("AIDA formulasi bilan <hl>sotuv matni</hl> 👇","Sen sotuv kopirayterisan. [mahsulot] uchun AIDA formatida matn yoz: diqqat, qiziqish, istak, harakat. Foydalari: [3 ta]. Auditoriya: [kim]. Yolg'on va'dasiz, oxirida aniq chaqiriq.",
 ["AIDA tuzilmasi","Real foydalar","Aniq chaqiriq"],132,"#sotuv #kopirayting #prompt #chatgpt #uzbekistan"),
("Muzokaraga <hl>AI bilan</hl> tayyorlaning 👇","Sen muzokara murabbiyisan. Mavzu: [narx oshishi]. Pozitsiyam: [fikrim]. Qarshi tomon e'tirozlari: [e'tirozlar]. Mashq ssenariysi, javob dalillari va kuchli xulosa tavsiyalarini ber.",
 ["Mashq ssenariysi","E'tirozlarga javoblar","Kuchli xulosa"],87,"#muzokara #biznes #prompt #chatgpt #uzbekistan"),
]
FULL=json.load(open('fullp.json'))
IT=[("PROMPT","Mijoz e'tirozlariga javob"),("n8n FAYL","Gmail to'lovlarini Google Sheets'ga yig'ish"),("ILOVA","Trello: kunlik vazifalar"),
("PROMPT","Instagram Reels uchun sotuvchi ssenariylar"),("n8n FAYL","WhatsApp lidlarini Sheets'ga saqlash va avto-javob"),("KOD","vcard: shaxsiy portfolio sayt"),
("VIDEO","n8n boshlovchilar kursi"),("PROMPT","Marketplace uchun mahsulot tavsifi"),("n8n FAYL","Gmail va AI bilan xatlarga avtomatik javob"),
("SAYT","n8n, Make, ClickUp"),("PROMPT","Mahsulot tannarxi va narxini hisoblash"),("n8n FAYL","AI bilan LinkedIn postlarini avtomatlashtirish"),
("KOD","split-pro: xarajatlarni bo'lishish ilovasi"),("PROMPT","Telegram kanal uchun 30 kunlik reja"),("ILOVA","Google Sheets"),
("n8n FAYL","Google Sheets orqali WhatsApp eslatmalar"),("PROMPT","Norozi mijozga uzr xabari"),("VIDEO","n8n'da birinchi workflow")]
rot=lambda k:IT[k:]+IT[:k]
BH=["Yopiq kanalda <hl>bir kunda</hl> nima chiqadi? 👇","Tayyor n8n fayllar, promptlar: <hl>ko'rsataman</hl> 👇","Har kuni <hl>12 ta</hl> foydali post. Mana misollar 👇",
    "Biznesingiz uchun <hl>tayyor vositalar</hl> 👇","Noldan izlamang: <hl>hammasi tayyor</hl> 👇","AI bilan ishlash uchun <hl>bitta kanal</hl> 👇","Kanal ichini <hl>ochib ko'rsataman</hl> 👇"]
V=json.load(open('cfg.json')); ids=[f'a{i}' for i in range(16,23)]+[f'b{i:02d}' for i in range(5,12)]; V=[v for v in V if v['id'] not in ids]
new=[]
for i,(h,p,r,pid,tags) in enumerate(A):
    H=2.2; te=round(H+0.35+min(5.6,len(p)/72),2); ra=round(te+1.3,2); E=round(ra+2.6,2)
    full=FULL[str(pid)].strip()
    new.append(dict(id=f"a{16+i}",fmt='A',accent='#FFD43B',accent2='#5B6CFF',pill="📌 SAQLAB QO'YING",hook=h,prompt=p,results=r,H=H,typeEnd=te,resAt=ra,E=E,T=round(E+2.8,2),
      end1="Yopiq kanalda <hl>har kuni</hl> shunday promptlar",chips=CH,enote="To'liq prompt pastdagi yozuvda 👇",
      caption=f"{pl(h).replace(' 👇','')} 👇\n\n📋 Prompt (nusxa oling):\n{full}\n\n{HOW}\n\n📌 Saqlab qo'ying, kerak bo'ladi. Do'stingizga ham yuboring.\n\n{FOOT}\n\n{tags}"))
BCAP=("{h}\n\nYopiq kanalda har kuni 12 ta yangi post chiqadi:\n💬 Tayyor promptlar: nusxa olib ishlatasiz\n⚙️ n8n shablon fayllari (.json): import qilasiz\n"
      "📱 Ilova va foydali saytlar tavsiyasi\n💻 Ochiq kod loyihalari (zip)\n🎥 Foydali video darslar\n\nNarxi: 100 000 so'm, bir martalik. Materiallarni ko'chirib bo'lmaydi, faqat a'zolar uchun.\n\n"
      "👉 Kirish: Telegram @A1Prompt_bot (profildagi havola)\n🆓 Avval bepul namunalarni ko'ring: t.me/AIPromptMasters\n\n#ai #prompt #n8n #telegram #uzbekistan")
for i,h in enumerate(BH):
    new.append(dict(id=f"b{5+i:02d}",fmt='B',accent='#3BE0FF',accent2='#7C4DFF',pill='🔒 YOPIQ KANAL ICHI',hook=h,items=rot((i*5+3)%18)[:14],
      counter="Har kuni <hl>12 ta</hl> yangi post",H=2.0,E=9.2,T=12.0,speed=285,end1="Hammasi <hl>bitta yopiq kanalda</hl>",chips=CH,enote="Bir martalik to'lov: 100 000 so'm",
      caption=BCAP.format(h=pl(h))))
V+=new; json.dump(V,open('cfg.json','w'),ensure_ascii=False,indent=1)
days=["05","06","07","08","09","10","11"]
plan=[]
for k,d in enumerate(days):
    plan.append(dict(id=f"b{5+k:02d}",publish_at=f"2026-11-{d}T07:30")); plan.append(dict(id=f"a{16+k}",publish_at=f"2026-11-{d}T23:00"))
json.dump(plan,open('plan_y.json','w'),indent=1)
for v in new: assert len(v['caption'])<2150,(v['id'],len(v['caption']))
print(len(new))
