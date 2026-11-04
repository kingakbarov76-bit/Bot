import json
FOOT=("🔒 Yopiq kanalda har kuni yangi promptlar, n8n shablon fayllari, ilovalar va kod loyihalari.\n"
      "👉 Telegram: @A1Prompt_bot (profildagi havola)\n🆓 Bepul namunalar: t.me/AIPromptMasters")
HOW="Qanday ishlatiladi: [ ] ichini o'zingiznikiga almashtiring va ChatGPT, Claude yoki Gemini'ga yuboring."
pl=lambda s:s.replace('<hl>','').replace('</hl>','')
CH=["💬 Promptlar","⚙️ n8n fayllar","📱 Ilovalar","💻 Kod loyihalar"]
A=[
("Ingliz tilidagi xatingizni <hl>AI tuzatsin</hl> 👇","Sen professional tarjimon va muharrirsan. Men istalgan tilda matn yuboraman. Uni grammatik xatosiz, professional ingliz tiliga tarjima qil va yaxshila. Ma'noni saqla, tushuntirish yozma, faqat tayyor matnni ber: [matningiz]",
 ["Xatosiz ingliz tili","Professional ohang","Faqat tayyor matn"],
 "Sen professional ingliz tili tarjimoni va matn muharririsan. Men senga istalgan tilda matn yuboraman. Sen tilni aniqlab, uni grammatik xatolarsiz, yuqori darajadagi (C1-C2 darajadagi) adabiy ingliz tiliga tarjima qilib va yaxshilab berasan. Asl ma'noni saqlagan holda, so'zlarni yanada jozibali va professional shaklga keltir. Hech qanday tushuntirish yozma, faqat tayyor va to'g'rilangan matnning o'zini javob sifatida qaytar. Mening biznesga oid birinchi matnim: [bu yerga ingliz tiliga tarjima qilinishi kerak bo'lgan matningizni yozing]","#ingliztili #prompt #chatgpt #tarjima #uzbekistan"),
("Mahsulot narxini <hl>to'g'ri hisoblang</hl> 👇","Sen moliyaviy maslahatchisan. Xomashyo: [summa]. Tayyorlash: [summa]. Qadoqlash va yetkazish: [summa]. Kutilgan foyda: [40%]. Soliq va qo'shimcha: [12%]. Tannarx va chakana narxni formula bilan jadvalda hisobla, qisqa tavsiya ber.",
 ["Tannarx jadvali","Tavsiya etilgan narx","Formula bilan, aniq"],
 "Sen tajribali moliyaviy maslahatchi va narx siyosati mutaxassisisan. Quyidagi ma'lumotlar asosida kichik biznesim uchun mahsulot tannarxi va tavsiya etilgan chakana narxini hisoblab ber:\n1. Xomashyo va materiallar narxi: [masalan: 100 000 so'm]\n2. Ishlab chiqarish yoki tayyorlashga ketgan vaqt/sarf: [masalan: 20 000 so'm]\n3. Qadoqlash va yetkazib berish xarajati: [masalan: 10 000 so'm]\n4. Kutilayotgan sof foyda ulushi (%): [masalan: 40%]\n5. Soliqlar va qo'shimcha xarajatlar (%): [masalan: 12%]\nHisob-kitobni aniq formula asosida jadval ko'rinishida ko'rsat va bozorda raqobatbardosh bo'lishi uchun qisqa tavsiya qo'sh.","#biznes #narx #prompt #chatgpt #uzbekistan"),
("Ish suhbatiga <hl>AI bilan</hl> tayyorlaning 👇","Sen ishga qabul qiluvchi mutaxassissan. Men nomzodman, lavozim: [sotuv menejeri]. Intervyu savollarini birma-bir ber va javobimni kut. Tushuntirish yozma, haqiqiy intervyudagidek gapir. Birinchi gapim: Salom.",
 ["Haqiqiy intervyu mashqi","Savollar birma-bir","Ishonch paydo bo'ladi"],
 "Sen professional ishga qabul qiluvchi mutaxassissan. Men nomzod bo'laman va sen menga [Lavozim, masalan: sotuv menejeri] lavozimi uchun intervyu savollarini berasan. Faqat intervyuyer rolida gapir. Barcha suhbatni birdaniga yozma, faqat savollarni birma-bir berib, javoblarimni kut. Hech qanday tushuntirish yozma. Haqiqiy intervyudagidek savollarni navbat bilan ber va javobimni kut. Mening birinchi gapim: Salom.","#ish #intervyu #prompt #chatgpt #uzbekistan"),
("Reklama kampaniyasini <hl>AI rejalashtirsin</hl> 👇","Sen reklama mutaxassisisan. [mahsulot yoki xizmat] uchun kampaniya tuz. Auditoriya: [18-30 yosh]. Kerak: 3 ta shior, O'zbekistonda ishlaydigan kanallar, savdoni oshiruvchi aksiya g'oyalari. Aniq formatda ber.",
 ["3 ta shior varianti","Mos reklama kanallari","Aksiya g'oyalari"],
 "Sen tajribali reklama mutaxassisisan. Maqsadim - [mahsulot yoki xizmat turi] uchun samarali reklama kampaniyasini yaratish. Auditoriyamiz [maqsadli auditoriya, masalan: 18-30 yoshli yoshlar]. Menga quyidagilarni tayyorlab ber: 1. Asosiy xabarlar va esda qolarli shiorlar (3 ta variant). 2. O'zbekiston bozorida samarali ishlaydigan media kanallar (ijtimoiy tarmoqlar, tashqi reklama va boshqalar). 3. Savdoni oshirish uchun qo'shimcha faolliklar yoki aksiyalar rejasi. Natijani aniq va tushunarli formatda taqdim et.","#reklama #marketing #prompt #chatgpt #uzbekistan"),
("Yetkazib beruvchidan <hl>chegirma</hl> so'rang 👇","Sen xaridlar menejerisan. [mahsulot] yetkazib beruvchisiga xat yoz. Hozirgi narx: [narx]. Maqsad: [yangi narx] yoki [30 kun kechiktirilgan to'lov]. Uzoq hamkorlik va hajm oshishini dalil qil. Rasmiy, hurmatli ohangda.",
 ["Tayyor rasmiy xat","Ishonarli dalillar","Hurmatli ohang"],
 "Sen tajribali xaridlar menejeri va muzokara ustasisan. Bizning [biznes turi] kichik biznesimiz uchun [mahsulot nomi] yetkazib beruvchisiga yuborish uchun professional xat yozib ber. Hozirgi narx [joriy narx] so'm. Biz bu narxni [maqsadli narx] so'mga tushirmoqchimiz yoki [qo'shimcha shart, masalan: 30 kunlik kechiktirilgan to'lov] olishni rejalashtirmoqdamiz. Xatda uzoq muddatli hamkorlik va hajmning oshishi mumkinligi haqida argumentlar keltirilsin. Javobni hurmat bilan yakunlanuvchi rasmiy elektron pochta shaklida tayyorlab ber.","#biznes #muzokara #prompt #chatgpt #uzbekistan"),
("Dangasalikni yengish uchun <hl>AI murabbiy</hl> 👇","Sen motivatsion murabbiysan. Maqsadim: [yangi mahsulot chiqarish]. Qiyinchiligim: [vaqt yetishmasligi]. Menga amaliy strategiya, qisqa motivatsiya va har kuni bajaradigan [3 ta] mashq ber. O'zbekiston sharoitini hisobga ol.",
 ["Amaliy strategiya","Kunlik mashqlar","Aniq reja"],
 "Sen professional motivatsion murabbiysan. Menga [maqsadim, masalan: yangi mahsulotni bozorga chiqarish] ustida ishlashda intizomni saqlashim va [duch kelayotgan qiyinchilik, masalan: vaqt yetishmasligi yoki dangasalik]ni yengishim uchun amaliy strategiyalar kerak. O'zbekiston kichik biznes bozori sharoitini inobatga olib, menga ijobiy motivatsiya ber, foydali maslahatlar yoz va kundalik bajarishim mumkin bo'lgan [vaqt oralig'i, masalan: 3 ta] amaliy mashqni taklif qil.","#motivatsiya #biznes #prompt #chatgpt #uzbekistan"),
]
D=[
("Instagram post <hl>yozolmayapsizmi?</hl>","Instagram post yoz","umumiy, hech kimga tegmaydigan matn","Sen SMM mutaxassisisan. [biznes] uchun 3 ta post yoz: muammo, foyda, chaqiriq. Har biri 4 qator, emoji me'yorida, auditoriya: [kim].","auditoriyaga mos 3 ta tayyor post","#instagram #smm #prompt #chatgpt #uzbekistan"),
("Mijoz narx so'rasa, <hl>nima deysiz?</hl>","Mijozga narx ayt","quruq raqam, mijoz ketib qoladi","Sen tajribali sotuvchisan. Mijoz narx so'radi: [mahsulot, narx]. Narxni qiymat bilan tushuntirib, 3 qatorli javob yoz, oxirida mijozga savol ber.","qiymat bilan tushuntirilgan javob","#sotuv #mijoz #prompt #chatgpt #uzbekistan"),
("Biznes g'oya kerakmi? <hl>To'g'ri so'rang</hl>","Menga biznes g'oya ber","hamma biladigan 10 ta umumiy g'oya","Sen biznes maslahatchisan. [shahar]da [byudjet] bilan boshlash mumkin bo'lgan 5 ta kichik biznes g'oyasini ber: xarajat, xavf, birinchi qadam. Jadvalda.","sizning byudjetingizga mos g'oyalar","#biznes #goya #prompt #chatgpt #uzbekistan"),
("Rasmiy xatni <hl>2 daqiqada</hl> yozing","Xat yozib ber","noaniq, kimga ekani tushunarsiz","Sen ish yozishmalari mutaxassisisan. [kimga] [maqsad] haqida rasmiy xat yoz: salom, sabab, taklif, xayrlashuv. 120 so'zgacha, hurmatli ohangda.","yuborishga tayyor rasmiy xat","#xat #ish #prompt #chatgpt #uzbekistan"),
("Ingliz tilini AI bilan <hl>to'g'ri o'rganing</hl>","Ingliz tilini o'rgat","tartibsiz ma'lumot, mashq yo'q","Sen ingliz tili o'qituvchisisan. Darajam: [A2]. Har kuni 10 ta yangi so'z, 3 ta misol gap va 5 savollik test ber. Bugungi mavzu: [mavzu].","har kunlik dars va test","#ingliztili #talim #prompt #chatgpt #uzbekistan"),
("Kontent reja tuzish <hl>qiyinmi?</hl>","Kontent reja tuz","nima qachon chiqishi noaniq","Sen SMM mutaxassisisan. [biznes] uchun 14 kunlik kontent reja tuz: kun, format (reels/story/post), mavzu, chaqiriq. Jadvalda ber.","14 kunlik aniq jadval","#smm #kontent #prompt #chatgpt #uzbekistan"),
("Taqdimotni AI bilan <hl>tez tayyorlang</hl>","Taqdimot qilib ber","tuzilmasiz, uzun matn","Sen taqdimot mutaxassisisan. [mavzu] bo'yicha 8 slaydli reja tuz: sarlavha, 3 punkt va slayd uchun rasm g'oyasi. Auditoriya: [kim].","8 slaydli tayyor reja","#taqdimot #talim #prompt #chatgpt #uzbekistan"),
("Kodingizda xato bormi? <hl>Bunday so'rang</hl>","Kodni tuzat","nima o'zgargani noma'lum","Sen tajribali dasturchisan. Quyidagi [til] kodidagi xatoni top, sababini oddiy tilda tushuntir va tuzatilgan kodni ber: [kod]","xato sababi va tuzatilgan kod","#dasturlash #kod #prompt #chatgpt #uzbekistan"),
]
V=json.load(open('cfg.json')); V=[v for v in V if v['id'] not in [f'a{i}' for i in range(10,16)]+[f'd{i:02d}' for i in range(7,15)]]
new=[]
for i,(h,p,r,full,tags) in enumerate(A):
    H=2.2; te=round(H+0.35+min(5.6,len(p)/72),2); ra=round(te+1.3,2); E=round(ra+2.6,2)
    new.append(dict(id=f"a{10+i}",fmt='A',accent='#FFD43B',accent2='#5B6CFF',pill="📌 SAQLAB QO'YING",hook=h,prompt=p,results=r,H=H,typeEnd=te,resAt=ra,E=E,T=round(E+2.8,2),
      end1="Yopiq kanalda <hl>har kuni</hl> shunday promptlar",chips=CH,enote="To'liq prompt pastdagi yozuvda 👇",
      caption=f"{pl(h).replace(' 👇','')} 👇\n\n📋 Prompt (nusxa oling):\n{full}\n\n{HOW}\n\n📌 Saqlab qo'ying, kerak bo'ladi. Do'stingizga ham yuboring.\n\n{FOOT}\n\n{tags}"))
for i,(h,bad,badRes,good,goodRes,tags) in enumerate(D):
    H=2.2; gb=4.9; te=round(gb+0.3+min(4.2,len(good)/62),2); E=round(te+1.9,2)
    new.append(dict(id=f"d{7+i:02d}",fmt='D',accent='#FF6B6B',accent2='#FFB020',pill='💡 PROMPT SIRI',hook=h,bad=bad,badRes=badRes,good=good,goodRes=goodRes,H=H,goodAt=gb,typeEnd=te,E=E,T=round(E+2.8,2),
      end1="Yopiq kanalda <hl>tayyor promptlar</hl> har kuni",chips=CH,enote="Siz faqat [ ] ichini to'ldirasiz",
      caption=f"{pl(h)}\n\n❌ \"{bad}\" deb so'rasangiz: {badRes}.\n✅ Rol, ma'lumot va format bersangiz: {goodRes}.\n\n📋 Tayyor prompt:\n{good}\n\n{HOW}\n\n📌 Saqlab qo'ying.\n\n{FOOT}\n\n{tags}"))
V+=new; json.dump(V,open('cfg.json','w'),ensure_ascii=False,indent=1)
order=[("2026-11-05","a10","d07"),("2026-11-06","d08","a11"),("2026-11-07","a12","d09"),("2026-11-08","d10","a13"),("2026-11-09","a14","d11"),("2026-11-10","d12","a15"),("2026-11-11","d13","d14")]
plan=[]
for day,x,y in order: plan+= [dict(id=x,publish_at=f"{day}T14:00"),dict(id=y,publish_at=f"{day}T21:30")]
json.dump(plan,open('plan_x.json','w'),indent=1)
for v in new: assert len(v['caption'])<2100,v['id']
print(len(new))
