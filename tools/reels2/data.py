import json
CH_A=["💬 Promptlar","⚙️ n8n fayllar","📱 Ilovalar","💻 Kod loyihalar"]
FOOT=("🔒 Yopiq kanalda har kuni yangi promptlar, n8n shablon fayllari, ilovalar va kod loyihalari.\n"
      "👉 Telegram: @A1Prompt_bot (bir martalik to'lov: 100 000 so'm)\n"
      "🆓 Bepul namunalar: t.me/AIPromptMasters")
HOW="Qanday ishlatiladi: [ ] ichini o'zingiznikiga almashtiring va ChatGPT, Claude yoki Gemini'ga yuboring."
plain=lambda s:s.replace('<hl>','').replace('</hl>','')

# ---------------- A: tayyor prompt sovg'a
A=[
dict(hook="Mijoz <hl>«qimmat»</hl> desa, AI'ga shuni yozing 👇",
 prompt="Sen tajribali sotuv menejerisan. Biznesim: [biznes turi]. Mahsulot: [nomi va narxi]. Mijoz shunday e'tiroz bildirdi: \"[e'tiroz matni]\". Menga 3 xil javob yoz: 1) yumshoq, 2) faktlarga asoslangan, 3) qisqa va do'stona. O'zbek tilida, 3-5 gap, bosimsiz, yolg'on va'dasiz.",
 results=["3 xil tayyor javob","Bosimsiz, hurmatli ohang","Nusxa olib yuborasiz"],
 full="Sen tajribali sotuv menejerisan. Mening biznesim: [biznes turi]. Xizmat/mahsulot: [nomi va narxi]. Mijozlarim: [kimlar].\nMijoz shunday e'tiroz bildirdi: \"[e'tiroz matni]\".\nMenga 3 xil javob yoz: 1) yumshoq va hamdard, 2) faktlarga asoslangan, 3) qisqa va do'stona.\nQoidalar: o'zbek tilida yoz, 3-5 gapdan oshirma, bosim o'tkazma, yolg'on va'da berma, oxirida bitta aniq keyingi qadamni taklif qil.",
 tags="#prompt #chatgpt #sotuv #biznes #uzbekistan"),
dict(hook="1 haftalik post rejasini <hl>AI tuzsin</hl> 👇",
 prompt="Sen ijtimoiy tarmoq mutaxassisisan. Biznesim: [biznes turi, shahar]. Auditoriya: [yosh, qiziqish]. Maqsad: [yangi mijoz jalb qilish]. 7 kunlik kontent reja tuz, jadvalda: kun, post turi, mavzu, 2 gaplik g'oya, chaqiriq. Sotuv postlari 2 tadan oshmasin.",
 results=["7 kunlik tayyor jadval","Har kunga mavzu va g'oya","Instagram va Telegram uchun"],
 full="Sen ijtimoiy tarmoq bo'yicha mutaxassissan. Mening biznesim: [biznes turi, shahar]. Auditoriya: [yosh, qiziqish]. Maqsad: [masalan, yangi mijoz jalb qilish].\nMenga 7 kunlik kontent reja tuz. Har bir kun uchun jadval ko'rinishida yoz: kun, post turi (rasm/video/hikoya/so'rovnoma), mavzu, 2 gaplik matn g'oyasi, chaqiriq (CTA).\nHammasi o'zbek tilida bo'lsin. Sotuv postlari 7 tadan 2 tadan oshmasin, qolganlari foydali va qiziqarli bo'lsin.",
 tags="#prompt #smm #kontent #instagram #uzbekistan"),
dict(hook="Mijozlar bir xil savolni <hl>qayta-qayta</hl> beradimi?",
 prompt="Sen mijozlarga xizmat mutaxassisisan. Biznesim: [tavsif]. Narxlar: [ro'yxat]. Ish vaqti: [vaqt]. Manzil: [manzil]. Shu ma'lumot asosida mijozlar ko'p beradigan 20 ta savol va qisqa, aniq javob yoz. Ma'lumot yetmasa, to'qima: \"Operatorimiz javob beradi\" de.",
 results=["20 ta tayyor savol-javob","Botga yoki pinga qo'yasiz","Har safar qayta yozmaysiz"],
 full="Sen mijozlarga xizmat ko'rsatish bo'yicha mutaxassissan. Mening biznesim: [tavsif]. Xizmatlar va narxlar: [ro'yxat]. Ish vaqti: [vaqt]. Manzil: [manzil]. To'lov usullari: [usullar]. Qaytarish/bekor qilish qoidalari: [qoidalar].\nShu ma'lumotlarga tayanib, mijozlar beradigan eng ko'p uchraydigan 20 ta savolni va ularga qisqa, aniq, xushmuomala javoblarni o'zbek tilida yoz.\nFaqat men bergan ma'lumotdan foydalan. Ma'lumot yetmasa, to'qima, o'rniga \"Operatorimiz javob beradi\" deb yoz.",
 tags="#prompt #chatgpt #mijoz #biznes #uzbekistan"),
dict(hook="Sotuv matni yozolmayapsizmi? <hl>Shu promptni</hl> oling 👇",
 prompt="Sen reklama matnlari mutaxassisisan. Mahsulot: [nomi]. Xususiyatlari: [3-5 ta]. Narxi: [narx]. Kim uchun: [mijoz]. Telegram uchun sotuv matni yoz: sarlavha, muammo, yechim, 3 ta foyda, chaqiriq. 800 belgigacha, mubolag'asiz. 2 ta variant ber.",
 results=["2 ta tayyor sotuv matni","Muammo → yechim → foyda","Mubolag'asiz, halol"],
 full="Sen reklama matnlari bo'yicha mutaxassissan. Mahsulot/xizmat: [nomi]. Asosiy xususiyatlari: [3-5 ta]. Narxi: [narx]. Kim uchun: [mijoz turi]. Mijoz muammosi: [muammo].\nTelegram uchun sotuv matni yoz: 1) e'tiborni tortadigan sarlavha, 2) muammo, 3) yechim, 4) 3 ta foyda, 5) chaqiriq. Uzunligi 800 belgidan oshmasin, o'zbek tilida, emoji me'yorida.\nMubolag'a qilma, tekshirib bo'lmaydigan va'dalar berma. Menga 2 ta variant ber.",
 tags="#prompt #sotuv #reklama #telegram #uzbekistan"),
dict(hook="Yangi mijozga <hl>birinchi xabarni</hl> AI yozsin 👇",
 prompt="Sen B2B savdo kopirayterisan. Yangi mijozga qisqa birinchi xabar yoz. Biznesim: [biznes]. Mijoz sohasi: [soha]. Unga foydam: [foyda]. Telegram yoki LinkedIn uchun, hurmat bilan boshlansin va aniq chaqiriq bilan tugasin. Faqat tayyor matnni ber.",
 results=["Qisqa, hurmatli xabar","Aniq chaqiriq bilan","Darhol yuborishga tayyor"],
 full="Sen professional B2B savdo kopirayteri va mijozlar bilan aloqa o'rnatish mutaxassisisan. Menga yangi potensial mijozga yuborish uchun qisqa va ta'sirli sovuq murojaat (cold outreach) xabarini yozib ber. Biznes turi: [biznesingizni yozing]. Mijozning sohasi: [mijoz faoliyati]. Taklif etilayotgan foyda: [mijozga nima foyda berasiz]. Xabar Telegram yoki LinkedIn orqali yuboriladi, shuning uchun u juda uzun bo'lmasin, hurmat bilan boshlansin va aniq harakatga chaqiruv (Call to Action) bilan tugasin. Natijani faqat tayyor xabar matni shaklida, ortiqcha so'zlarsiz ber.",
 tags="#prompt #savdo #mijoz #biznes #uzbekistan"),
dict(hook="Tijoriy taklifni <hl>AI bilan</hl> tez tayyorlang 👇",
 prompt="Sen savdo mutaxassisisan. [mahsulot yoki xizmat] uchun tijoriy taklif yoz. Mijoz muammosi: [muammo]. Narx: [narx], muddat: [muddat]. Tuzilma: salom va muammo, yechimimiz, narx va muddat, keyingi qadam. 600-800 belgi, faqat faktlar.",
 results=["Tayyor tijoriy taklif","Rasmiy, ammo samimiy","Faqat faktlarga tayangan"],
 full="Sen professional kopirayter va savdo bo'yicha mutaxassissan. Menga [mahsulot yoki xizmat nomi] uchun potensial mijozga yuboriladigan tijoriy taklif matnini yozib ber. Mijozning asosiy muammosi: [mijozning og'riqli nuqtasi]. Taklifning narxi: [narx yoki shartlar] va u [muddat] ichida bajariladi. Matn o'zbek tilida, rasmiy, ammo samimiy ohangda bo'lsin. Tuzilishi quyidagicha bo'lsin: 1) Salomlashish va mijoz muammosini tushunish; 2) Bizning yechim va afzalliklarimiz; 3) Aniq narx va muddatlar; 4) Keyingi qadamga chaqiruv (Call to Action). Matn hajmi 600-800 belgidan oshmasin va ortiqcha maqtanchoq so'zlarsiz, faqat faktlarga tayansin.",
 tags="#prompt #biznes #savdo #chatgpt #uzbekistan"),
dict(hook="Reels uchun ssenariy <hl>topolmayapsizmi?</hl>",
 prompt="Sen Instagram marketing mutaxassisisan. [mahsulot yoki xizmat] uchun 3 ta qisqa Reels ssenariysi yoz. Har biri: 1) ilk 3 soniyadagi ilgak, 2) muammo va yechim, 3) chaqiriq. Auditoriya: [masalan, talabalar]. Sodda o'zbek tilida, yolg'on va'dalarsiz.",
 results=["3 ta tayyor ssenariy","Ilgak + yechim + chaqiriq","Kameraga olishga tayyor"],
 full="Sen Instagram marketing va kontent yaratish bo'yicha professional mutaxassissan. Menga [mahsulot yoki xizmat turi] uchun 3 ta qisqa Instagram Reels ssenariysi yozib ber. Har bir ssenariy quyidagi qismlardan iborat bo'lsin: 1. Ilgak (kadrdagi ilk 3 soniyada tomoshabinni ushlab qoladigan gap yoki harakat). 2. Asosiy qism (muammo va bizning yechimimiz, 20-30 soniya). 3. Harakatga chaqiruv (izoh yozish yoki buyurtma berishga undash). Ssenariylar tili sodda, samimiy va o'zbek tilining lotin alifbosida, biznesimning maqsadli auditoriyasi bo'lgan [auditoriya, masalan: yosh onalar / talabalar] uchun tushunarli bo'lsin. Ortiqcha va'dalar va yolg'on ma'lumotlarsiz, faqat real foydani ko'rsat.",
 tags="#prompt #reels #instagram #smm #uzbekistan"),
dict(hook="Telegram kanalingizga <hl>30 kunlik</hl> reja 👇",
 prompt="Sen SMM mutaxassisisan. [biznes turi] uchun Telegram kanalga 30 kunlik kontent reja tuz. Auditoriya: [auditoriya]. Post turlari: sotuvchi, foydali, ko'ngilochar, interaktiv. Har kunga mavzu, qisqa mazmun va chiqish vaqti. Jadvalda, o'zbek tilida.",
 results=["30 kunlik jadval","Har kunga mavzu va vaqt","4 xil post turi"],
 full="Sen tajribali SMM mutaxassisisan. [Biznes turi yoki mahsulot] bilan shug'ullanuvchi kichik biznesimiz uchun Telegram kanalimizga 30 kunlik kontent reja tuzib ber. Auditoriyamiz: [maqsadli auditoriya, masalan: ayollar, yoshlar]. Kontent reja quyidagi post turlarini o'z ichiga olsin: sotuvchi, foydali (ekspertiza), ko'ngilochar va interaktiv postlar. Har bir kun uchun post mavzusi, qisqacha mazmuni va eng yaxshi chiqish vaqtini aniq ko'rsat. Javobni jadval ko'rinishida, o'zbek tilida ber.",
 tags="#prompt #telegram #smm #kontent #uzbekistan"),
dict(hook="Mijoz <hl>norozi</hl> bo'ldimi? Shu promptni ishlating 👇",
 prompt="Sen mijozlar bilan muloqot mutaxassisisan. Norozi mijozga uzr xabarini yoz. Mijoz ismi: [ism]. Muammo: [masalan, buyurtma kechikdi]. Shikoyati: [matn]. Yechim: [chegirma yoki qaytarish]. Hurmat bilan, ortiqcha va'dasiz, qisqa yoz.",
 results=["Samimiy uzr xabari","Aniq yechim bilan","Vaziyatni yumshatadi"],
 full="Sen mijozlar bilan muloqot qilish va inqirozli vaziyatlarni boshqarish bo'yicha tajribali mutaxassissan. Quyidagi ma'lumotlar asosida norozi mijozga yuborish uchun samimiy va professional uzr so'rash xabarini yoz:\n- Mijoz ismi: [Mijoz ismi]\n- Yuzaga kelgan muammo: [Masalan: buyurtma kechikdi yoki sifatsiz chiqdi]\n- Mijozning e'tirozi: [Mijoz shikoyati]\n- Taklif etilayotgan yechim: [Masalan: pulini qaytarish, bepul yetkazib berish yoki chegirma]\nQoidalar: O'zbek tilida, hurmat bilan, ortiqcha va'dalarsiz, qisqa va tushunarli yoz. Xabar oxirida shaxsan bog'lanishim uchun raqam qoldiradigan joy bo'lsin.",
 tags="#prompt #mijoz #servis #biznes #uzbekistan"),
dict(hook="Uzum yoki OLX uchun <hl>mahsulot tavsifi</hl> 👇",
 prompt="Sen e-commerce kopirayterisan. [Mahsulot nomi] uchun Uzum Market va OLX'ga mos tavsif yoz. Xususiyatlari: [ro'yxat]. Tuzilma: jozibali kirish, 3-4 afzallik, texnik xususiyatlar, chaqiriq. Ravon o'zbek tilida, kalit so'zlar bilan, 600-900 belgi.",
 results=["Marketplace uchun tavsif","Kalit so'zlar bilan","Nusxa olib joylaysiz"],
 full="Sen tajribali e-commerce kopirayter va marketplace SEO mutaxassisisan. Menga [Mahsulot nomi] uchun Uzum Market va OLX talablariga mos, xaridorlarni tezda sotib olishga undaydigan mahsulot tavsifini yozib ber. Mahsulotning asosiy xususiyatlari: [xususiyatlarni yozing]. Tavsif quyidagi qismlardan iborat bo'lsin: 1. Qisqacha jozibali kirish qismi. 2. Asosiy afzalliklari va foydalanish sohasi (3-4 ta punkt). 3. Texnik xususiyatlari. 4. Xaridorlar uchun chaqiruv (Call to action). Matn ravon o'zbek tilida, imlo qoidalariga rioya qilingan holda, qidiruv tizimlari (SEO) uchun mos kalit so'zlar bilan boyitilib yozilsin. Hajmi 600-900 belgi oralig'ida bo'lsin.",
 tags="#prompt #uzum #olx #marketplace #uzbekistan"),
]
# ---------------- D: oddiy savol va tayyor prompt
D=[
dict(hook="ChatGPT <hl>yomon javob</hl> beryaptimi? Sababi bitta",
 bad="Menga reklama yozib ber",badRes="umumiy, hamma uchun bir xil matn",
 good="Sen SMM mutaxassisisan. [mahsulot] uchun Instagram reklama matni yoz. Auditoriya: [18-30 yosh]. 3 variant: qisqa, hikoya, savol bilan. Oxirida aniq chaqiriq.",
 goodRes="aniq, ishlatsa bo'ladigan 3 variant",tags="#chatgpt #prompt #reklama #smm #uzbekistan"),
dict(hook="AI'dan <hl>to'g'ri</hl> so'rashni bilasizmi?",
 bad="Biznes reja yoz",badRes="uzun, umumiy, foydasi kam",
 good="Sen biznes maslahatchisan. [shahar]da [biznes turi] ochmoqchiman, byudjet [summa]. Xarajatlar, narx, birinchi 3 oy rejasi va xavflarni jadvalda yoz. Taxminlarni alohida belgila.",
 goodRes="sizning holatingizga mos reja",tags="#chatgpt #biznes #prompt #startup #uzbekistan"),
dict(hook="Bir xil AI, <hl>ikki xil natija</hl>. Farqi nimada?",
 bad="Mijozga javob yoz",badRes="quruq va sovuq javob",
 good="Sen sotuv menejerisan. Mijoz \"[e'tiroz]\" dedi. Mahsulot: [nomi, narxi]. 3 xil javob yoz: yumshoq, faktli, qisqa. Har biri 3-5 gap, bosimsiz.",
 goodRes="3 ta tayyor, iliq javob",tags="#chatgpt #sotuv #prompt #mijoz #uzbekistan"),
dict(hook="AI bilan o'qiysizmi? <hl>Bunday</hl> so'rang",
 bad="Python o'rgat",badRes="tartibsiz, qayerdan boshlash noaniq",
 good="Sen sabrli o'qituvchisan. Python'ni noldan o'rganmoqchiman, kuniga [30 daqiqa] vaqtim bor. 4 haftalik reja tuz: har kunga mavzu, mashq va tekshiruv savoli. Oddiy o'zbek tilida.",
 goodRes="shaxsiy, kunma-kun o'quv reja",tags="#python #dasturlash #chatgpt #prompt #uzbekistan"),
dict(hook="ChatGPT tarjimasi <hl>g'alati</hl> chiqyaptimi?",
 bad="Inglizchaga tarjima qil",badRes="so'zma-so'z, g'alati jumlalar",
 good="Sen professional tarjimonsan. Matnni ingliz tiliga biznes xati ohangida, grammatik xatosiz tarjima qil. Ma'noni saqla, tushuntirish yozma, faqat tayyor matnni ber: [matn]",
 goodRes="toza, professional tarjima",tags="#ingliztili #tarjima #chatgpt #prompt #uzbekistan"),
dict(hook="Rezyume yozish <hl>qiyinmi?</hl> AI'ga bunday yozing",
 bad="Rezyume yoz",badRes="shablon, sizga o'xshamaydi",
 good="Sen HR mutaxassisisan. Tajribam: [ish joylari, yillar]. Ko'nikmalarim: [ro'yxat]. [lavozim] uchun 1 sahifalik rezyume yoz: qisqa xulosa, natijali tajriba, ko'nikmalar. Aniq va qisqa.",
 goodRes="lavozimga mos rezyume",tags="#rezyume #ish #chatgpt #prompt #uzbekistan"),
dict(hook="Narxni qanday qo'yishni <hl>bilmayapsizmi?</hl>",
 bad="Narx qancha bo'lsin?",badRes="\"bozorga qarab\" degan javob",
 good="Sen moliyaviy maslahatchisan. Xomashyo: [summa]. Ish: [summa]. Yetkazish: [summa]. Kutilgan foyda: [40%]. Tannarx va chakana narxni formula bilan jadvalda hisobla, qisqa tavsiya ber.",
 goodRes="aniq hisob-kitob jadvali",tags="#biznes #narx #chatgpt #prompt #uzbekistan"),
]
# ---------------- B: kanal ichi (haqiqiy post sarlavhalari)
IT=[("PROMPT","Mijoz e'tirozlariga javob"),("n8n FAYL","Gmail to'lovlarini Google Sheets'ga yig'ish"),("ILOVA","Trello: kunlik vazifalar"),
("PROMPT","Instagram Reels uchun sotuvchi ssenariylar"),("n8n FAYL","WhatsApp lidlarini Sheets'ga saqlash va avto-javob"),("KOD","vcard: shaxsiy portfolio sayt"),
("VIDEO","n8n boshlovchilar kursi"),("PROMPT","Marketplace uchun mahsulot tavsifi"),("n8n FAYL","Gmail va AI bilan xatlarga avtomatik javob"),
("SAYT","n8n, Make, ClickUp"),("PROMPT","Mahsulot tannarxi va narxini hisoblash"),("n8n FAYL","AI bilan LinkedIn postlarini avtomatlashtirish"),
("KOD","split-pro: xarajatlarni bo'lishish ilovasi"),("PROMPT","Telegram kanal uchun 30 kunlik reja"),("ILOVA","Google Sheets"),
("n8n FAYL","Google Sheets orqali WhatsApp eslatmalar"),("PROMPT","Norozi mijozga uzr xabari"),("VIDEO","n8n'da birinchi workflow")]
def rot(k): return IT[k:]+IT[:k]
B=[
dict(hook="100 000 so'mga <hl>nima</hl> olasiz? 👇",items=rot(0)[:14]),
dict(hook="Yopiq kanal <hl>ichida</hl> nima bor? Ko'rsataman 👇",items=rot(4)[:14]),
dict(hook="Kuniga <hl>12 ta</hl> yangi post. Mana ulardan bir qismi 👇",items=rot(8)[:14]),
dict(hook="Prompt, n8n fayl, ilova: <hl>hammasi bir joyda</hl>",items=rot(12)[:14]),
dict(hook="AI bilan ishlaysizmi? <hl>Bu kanal</hl> siz uchun 👇",items=rot(2)[:14]),
]
# ---------------- C: bonus dasturi
STEPS=[["Botdan havola oling","«Referal havolam» tugmasi"],["Do'stingizga yuboring","U yopiq kanalga to'lov qiladi"],["Balansga +10 000 so'm","To'lovi tasdiqlangach yoziladi"]]
C=[
dict(hook="Do'stingiz obuna bo'lsa, sizga <hl>10 000 so'm</hl>"),
dict(hook="Kanalga kirmasdan ham <hl>bonus</hl> yig'sa bo'ladi",step1="Kanalga kirmasangiz ham bo'ladi"),
dict(hook="Havolani ulashing, <hl>bonus</hl> oling. Shartlari 👇"),
dict(hook="5 do'st = <hl>50 000 so'm</hl>. Qanday ishlaydi?"),
dict(hook="Bonus dasturi: <hl>halol</hl> shartlar bilan 👇"),
dict(hook="Do'stlaringiz AI'ga qiziqadimi? <hl>Havolangizni</hl> ulashing"),
]
def ccap(h):
    return (f"{plain(h)} 🤝\n\nQanday ishlaydi:\n1) Telegram'da @A1Prompt_bot'ga kiring, «Referal havolam» tugmasidan shaxsiy havola oling.\n"
            "2) Havolani AI'ga qiziqadigan do'stlaringizga yuboring.\n3) Do'stingiz yopiq kanalga to'lov qilsa va to'lovi tasdiqlansa, balansingizga 10 000 so'm yoziladi.\n\n"
            "💸 Balans 50 000 so'mga yetsa kartaga yechasiz (har 15 kunda 1 marta).\n✅ Yopiq kanalga kirmagan bo'lsangiz ham qatnashasiz.\n"
            "⚠️ Daromad kafolatlanmaydi: bonus faqat tasdiqlangan to'lovdan yoziladi.\n\n"
            "Yopiq kanalda nima bor: har kuni yangi promptlar, n8n shablon fayllari, ilovalar va kod loyihalari.\n🆓 Bepul namunalar: t.me/AIPromptMasters\n\n"
            "#bonus #telegram #ai #prompt #uzbekistan")
V=[]
for i,d in enumerate(A):
    n=len(d['prompt']); H=2.2; te=round(H+0.35+min(5.6,n/72),2); ra=round(te+1.3,2); E=round(ra+2.6,2)
    V.append(dict(id=f"a{i:02d}",fmt='A',accent='#FFD43B',accent2='#5B6CFF',pill='📌 SAQLAB QO\'YING',hook=d['hook'],prompt=d['prompt'],results=d['results'],
      H=H,typeEnd=te,resAt=ra,E=E,T=round(E+2.8,2),end1="Yopiq kanalda <hl>har kuni</hl> shunday promptlar",chips=CH_A,enote="To'liq prompt pastdagi yozuvda 👇",
      caption=f"{plain(d['hook']).replace(' 👇','')} 👇\n\n📋 Prompt (nusxa oling):\n{d['full']}\n\n{HOW}\n\n📌 Saqlab qo'ying, kerak bo'ladi. Do'stingizga ham yuboring.\n\n{FOOT}\n\n{d['tags']}"))
for i,d in enumerate(D):
    n=len(d['good']); H=2.2; gb=4.9; te=round(gb+0.3+min(4.2,n/62),2); E=round(te+1.9,2)
    V.append(dict(id=f"d{i:02d}",fmt='D',accent='#FF6B6B',accent2='#FFB020',pill='💡 PROMPT SIRI',hook=d['hook'],bad=d['bad'],badRes=d['badRes'],good=d['good'],goodRes=d['goodRes'],
      H=H,goodAt=gb,typeEnd=te,E=E,T=round(E+2.8,2),end1="Yopiq kanalda <hl>tayyor promptlar</hl> har kuni",chips=CH_A,enote="Siz faqat [ ] ichini to'ldirasiz",
      caption=f"{plain(d['hook'])}\n\n❌ \"{d['bad']}\" deb so'rasangiz: {d['badRes']}.\n✅ Rol, ma'lumot va format bersangiz: {d['goodRes']}.\n\n📋 Tayyor prompt:\n{d['good']}\n\n{HOW}\n\n📌 Saqlab qo'ying.\n\n{FOOT}\n\n{d['tags']}"))
for i,d in enumerate(B):
    V.append(dict(id=f"b{i:02d}",fmt='B',accent='#3BE0FF',accent2='#7C4DFF',pill='🔒 YOPIQ KANAL ICHI',hook=d['hook'],items=d['items'],
      counter="Har kuni <hl>12 ta</hl> yangi post",H=2.0,E=9.2,T=12.0,speed=285,
      end1="Hammasi <hl>bitta yopiq kanalda</hl>",chips=CH_A,enote="Bir martalik to'lov: 100 000 so'm",
      caption=(f"{plain(d['hook']).replace(' 👇','')} 👇\n\nYopiq kanalda har kuni 12 ta yangi post chiqadi:\n💬 Tayyor promptlar: nusxa olib ishlatasiz\n⚙️ n8n shablon fayllari (.json): import qilasiz\n"
               "📱 Ilova va foydali saytlar tavsiyasi\n💻 Ochiq kod loyihalari (zip)\n🎥 Foydali video darslar\n\nNarxi: 100 000 so'm, bir martalik. Materiallarni ko'chirib bo'lmaydi, faqat a'zolar uchun.\n\n"
               "👉 Kirish: Telegram @A1Prompt_bot\n🆓 Avval bepul namunalarni ko'ring: t.me/AIPromptMasters\n\n#ai #prompt #n8n #telegram #uzbekistan")))
for i,d in enumerate(C):
    st=[s[:] for s in STEPS]
    if d.get('step1'): st[0][1]=d['step1']
    V.append(dict(id=f"c{i:02d}",fmt='C',accent='#3DDC84',accent2='#00B3FF',pill='👥 BONUS DASTURI',hook=d['hook'],steps=st,
      calcTitle="Hisob <hl>oddiy:</hl>",calc=[["1 do'st","10 000 so'm"],["3 do'st","30 000 so'm"],["5 do'st","50 000 so'm"]],
      rules=[["💸","50 000 so'mdan kartaga yechasiz"],["🗓","Har 15 kunda 1 marta"],["⚠️","Kafolat yo'q: faqat tasdiqlangan to'lovdan"]],
      H=2.2,calcAt=5.6,E=11.0,T=13.8,end1="Shaxsiy havolangizni <hl>botdan</hl> oling",chips=["👥 Referal havola","💰 Balans botda","💸 Kartaga yechish"],
      enote="⚠️ Daromad kafolatlanmaydi",caption=ccap(d['hook'])))
json.dump(V,open('cfg.json','w'),ensure_ascii=False,indent=1)
for v in V: assert len(v['caption'])<2100,(v['id'],len(v['caption']))
print(len(V),[ (v['id'],v['T']) for v in V])
