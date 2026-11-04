# Barcha postlarni yig'ib, aralash tartibda items_all.json ga yozadi + zip fayllarni tayyorlaydi
import json, os, shutil, zipfile
P = "/home/claude/bot/paid"
os.makedirs(f"{P}/zip", exist_ok=True)

def zipdir(slug):
    out = f"{P}/zip/{slug}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(f"{P}/src/{slug}"):
            for f in files:
                if f.endswith((".pyc",)) or "__pycache__" in root or f == "orders.db": continue
                full = os.path.join(root, f); z.write(full, os.path.join(slug, os.path.relpath(full, f"{P}/src/{slug}")))
    return out

GET = "\n\n📥 <b>Faylni olish:</b> pastdagi tugmani bosing, bot faylni shaxsiy chatga yuboradi."

items = json.load(open(f"{P}/items_text.json"))

# ---------------------------------------------------------------- KOD (10)
CODE = [
("telegram-buyurtma-bot", "Telegram buyurtma bot (Python, kutubxonasiz)", None,
 "Kafe, do'kon yoki xizmat uchun tayyor bot: menyu → savat → ism, telefon, manzil → buyurtma bazaga yoziladi va sizga keladi.",
 ["Python 3.9+, hech qanday pip o'rnatish kerak emas", "Buyurtmalar SQLite bazada saqlanadi", "Telefon raqami tekshiriladi", "Internetsiz test fayli bor: <code>python test_bot.py</code>"],
 "Mahsulotlaringizni <code>bot.py</code> dagi PRODUCTS ro'yxatiga yozing, @BotFather'dan token oling va ishga tushiring. Batafsil README.md'da.", "Python"),
("excel-hisobot", "CSV → chiroyli Excel hisobot (grafik bilan)", "code_excel.jpg",
 "Sotuv ro'yxatini (CSV) 1 soniyada formulali, grafikli Excel hisobotga aylantiradi: mahsulotlar bo'yicha tushum, oyma-oy dinamika.",
 ["3 varaq: ma'lumot, mahsulotlar + grafik, oylar", "Namuna CSV fayl bilan", "Kassa, marketpleys yoki Google Sheets eksporti bilan ishlaydi"],
 "<code>pip install openpyxl</code>, keyin <code>python report.py sales.csv report.xlsx</code>.", "Python"),
("rasm-ommaviy", "Yuzlab rasmni bir buyruqda kichraytirish + logo yozuvi", None,
 "Mahsulot rasmlarini Instagram yoki sayt uchun bir zumda tayyorlaydi: o'lchamni kichraytiradi, burchagiga brend yozuvini qo'yadi, JPG/PNG/WEBP ga o'giradi.",
 ["Asl rasmlar o'zgarmaydi", "Telefon rasmining burilishini avtomatik to'g'rilaydi", "WEBP: sayt uchun 3 baravar yengil"],
 "<code>pip install pillow</code>, keyin <code>python images.py rasmlar natija --width 1080 --watermark \"@dokonim\"</code>", "Python"),
("pdf-vositalar", "PDF vositalari: birlashtirish, bo'lish, parol qo'yish", None,
 "Hujjatlarni onlayn saytlarga yuklamasdan (maxfiylik!) o'z kompyuteringizda PDF bilan ishlash: birlashtirish, sahifalarga bo'lish, kerakli sahifalarni ajratish, aylantirish, parol qo'yish.",
 ["6 ta buyruq, bitta fayl", "AES-256 parol himoyasi", "Sahifa raqamini xato yozsangiz, tushunarli xabar beradi"],
 "<code>pip install pypdf cryptography</code>, buyruqlar jadvali README.md'da.", "Python"),
("hisob-faktura-pdf", "Hisob-faktura (invoice) PDF generatori", "file_Hisob_faktura.jpg",
 "JSON fayldagi ma'lumotdan chiroyli PDF hisob-faktura yasaydi: sotuvchi, xaridor, mahsulotlar jadvali, jami, QQS, imzo joyi.",
 ["O'zbekcha harflar to'g'ri chiqadi", "QQS foizi va valyuta sozlanadi", "Mijozlarga yuborishga tayyor PDF"],
 "<code>pip install reportlab</code>, <code>invoice.json</code> ni to'ldiring va <code>python invoice.py invoice.json hisob.pdf</code>.", "Python"),
("forma-telegramga", "Saytdagi ariza formasi → to'g'ridan-to'g'ri Telegramingizga", "code_forma.jpg",
 "Mijoz saytda ism, telefon, izoh qoldiradi, sizga Telegram'da darhol xabar keladi. Bot token sayt kodida ko'rinmaydi: xabar bepul Cloudflare Worker orqali o'tadi.",
 ["Tayyor chiroyli forma (mobilga mos)", "Spam-botlardan himoya", "Cloudflare Worker kodi + 15 daqiqalik sozlash yo'riqnomasi"],
 "README.md'dagi 6 qadamni bajaring: bot yarating, worker'ni joylang, manzilni formaga yozing.", "HTML + JavaScript"),
("xarajat-hisobchi", "Shaxsiy xarajatlar hisobchisi (bitta HTML fayl)", "code_xarajat.jpg",
 "Telefon yoki kompyuterda ishlaydigan ilova: xarajatlarni toifa bilan yozasiz, oy bo'yicha jami, kunlik o'rtacha va toifalar diagrammasini ko'rasiz.",
 ["Internet va ro'yxatdan o'tish kerak emas", "Ma'lumot faqat sizning brauzeringizda", "Excel uchun CSV yuklab olish"],
 "<code>index.html</code> ni brauzerda oching. Telefonda «Bosh ekranga qo'shish» qilsangiz, ilova kabi ishlaydi.", "HTML + JavaScript"),
("fayl-saralash", "«Yuklab olinganlar» papkasini avtomatik tartiblash", None,
 "Yuzlab aralash faylni turiga qarab papkalarga ajratadi: Rasmlar, Videolar, Hujjatlar, Jadvallar, Arxivlar, Dasturlar va boshqalar.",
 ["Avval sinov rejimi (--dry-run): hech narsa ko'chirilmaydi", "Bir xil nomli faylni ustidan yozmaydi", "--undo bilan hammasi joyiga qaytadi"],
 "<code>python organize.py \"C:/Users/Ism/Downloads\" --dry-run</code>, keyin shu buyruqni --dry-run'siz.", "Python"),
("valyuta-kursi", "Markaziy bank valyuta kursi + konvertor", None,
 "cbu.uz'dan rasmiy kurslarni oladi, istalgan summani o'giradi (100 USD → so'm, so'm → EUR) va kurslar tarixini CSV'ga yig'adi.",
 ["Qo'shimcha kutubxona kerak emas", "Nominali 10 yoki 100 bo'lgan valyutalar ham to'g'ri hisoblanadi", "Internetsiz test fayli bilan"],
 "<code>python rates.py 100 USD</code>. cbu.uz O'zbekiston ichidan ishonchli ochiladi.", "Python"),
("test-yaratuvchi", "Test (quiz) yaratuvchi: o'qituvchilar uchun", "code_test.jpg",
 "Savollarni oddiy matn qilib yozasiz, bir tugma bilan vaqtli, aralashtirilgan test tayyor bo'ladi. Oxirida ball, foiz va xato javoblar tahlili chiqadi.",
 ["To'g'ri javob oldiga * qo'yish kifoya", "Taymer va aralashtirish", "ChatGPT'dan formatga mos savollar olish maslahati README'da"],
 "<code>index.html</code> ni oching, savollarni yozing, «Testni boshlash».", "HTML + JavaScript"),
]
for slug, t, img, what, feats, how, lang in CODE:
    zipdir(slug)
    body = (f"💻 <b>Kod: {t}</b>\n\n{what}\n\n<b>Ichida:</b>\n" + "\n".join(f"✅ {f}" for f in feats) +
            f"\n\n🛠 <b>Til:</b> {lang}. Kod va izohlar asl (inglizcha) holida, yo'riqnoma (README.md) o'zbekcha.\n▶️ <b>Ishga tushirish:</b> {how}\n🧪 Kanalga qo'yishdan oldin sinab ko'rilgan." + GET + "\n#kod")
    items.append(dict(cat="code", title=t, body=body, photo=(f"paid/img/{img}" if img else None), file_src=f"gh:paid/zip/{slug}.zip", file_name=f"{slug}.zip"))

# ---------------------------------------------------------------- SAYTLAR (5)
SITES = [
("sayt-kafe", "Kafe / restoran sayti: onlayn menyu va savat", "Toifali menyu, savat, miqdorni o'zgartirish va buyurtmani bir tugma bilan Telegram yoki WhatsApp'ga yuborish. Manzil, ish vaqti, yetkazib berish bloklari."),
("sayt-oquv-markaz", "O'quv markazi sayti: kurslar va yozilish", "Kurslar kartochkalari (narx, davomiylik, mavzular), «Qanday o'qitamiz» bloki va sinov darsiga yozilish formasi (ma'lumot Telegram'ga)."),
("sayt-barbershop", "Barbershop / salon sayti: onlayn yozilish", "Xizmatlar va narxlar, ishlar galereyasi, kun va vaqtni tanlab yozilish (o'tib ketgan vaqtlar ko'rinmaydi). Qorong'i premium dizayn."),
("sayt-portfolio", "Shaxsiy portfolio sayti", "Dasturchi, dizayner yoki SMM mutaxassisi uchun: ishlar ro'yxati toifa filtri bilan, ko'nikmalar, tajriba va aloqa bloki."),
("sayt-dokon", "Internet do'kon katalogi: savat va buyurtma", "Qidiruv, toifa filtri, narx bo'yicha saralash, chegirma belgisi, savat va buyurtmani Telegram/WhatsApp orqali qabul qilish."),
]
for slug, t, what in SITES:
    zipdir(slug)
    body = (f"🌐 <b>Tayyor sayt: {t}</b>\n\n{what}\n\n"
            "✅ Telefon va kompyuterga moslashgan\n✅ Kutubxona va internet kerak emas: oddiy HTML, CSS, JS\n✅ Matn, narx va ranglar bitta joydan o'zgaradi\n"
            "✅ Netlify yoki GitHub Pages'ga <b>bepul</b> joylash yo'riqnomasi bilan\n🧪 Barcha tugmalar brauzerda sinab ko'rilgan.\n\n"
            "💼 <b>Pul ishlash g'oyasi:</b> shu shablonni mahalladagi kafe, salon yoki do'konga moslab, sayt qilib bering." + GET + "\n#sayt")
    items.append(dict(cat="site", title=t, body=body, photo=f"paid/img/{slug}.jpg", file_src=f"gh:paid/zip/{slug}.zip", file_name=f"{slug}.zip"))

# ---------------------------------------------------------------- DIZAYN SHABLONLAR (5)
DES = [
("dizayn-instagram-aksiya", "Instagram aksiya posti (1080×1080)", "Chegirma, aksiya va yangi mahsulot e'loni uchun tayyor post. Matn va ranglarni o'zgartirib, bir tugma bilan PNG yuklab olasiz."),
("dizayn-vizitka", "Vizitka (90×50 mm, chop etishga tayyor)", "Ism, lavozim, telefon, Telegram, manzil va rangni kiritasiz: chop etish uchun PNG yoki PDF tayyor. Bosmaxonaga to'g'ridan-to'g'ri berasiz."),
("dizayn-sertifikat", "Sertifikat / diplom (A4)", "O'quv markazlari, kurslar va tadbirlar uchun. Ismni almashtirib, har bir o'quvchiga alohida sertifikat chiqarasiz (PNG yoki PDF)."),
("dizayn-narxlar", "Narxlar ro'yxati / menyu (A4)", "Salon, kafe yoki xizmatlar uchun devorga osiladigan narxlar varag'i. 8 ta qator, ranglar va nomi o'zgaradi, A4 chop etiladi."),
("dizayn-stories", "Stories e'lon (1080×1920)", "Instagram va Telegram stories uchun yorqin gradientli e'lon: yangi kurs, aksiya, tadbir. Matn, tugma va ranglar o'zgaradi."),
]
for slug, t, what in DES:
    zipdir(slug)
    body = (f"🎨 <b>Dizayn shabloni: {t}</b>\n\n{what}\n\n"
            "✅ Dastur o'rnatish shart emas: <code>index.html</code> ni brauzerda ochasiz\n✅ Chapda maydonlar, o'ngda tayyor dizayn darhol o'zgaradi\n"
            "✅ PNG yuklab olish, SVG esa Figma, Canva yoki Inkscape'da erkin tahrirlash uchun\n🧪 PNG va SVG yuklab olish sinab ko'rilgan." + GET + "\n#shablon #dizayn")
    items.append(dict(cat="design", title=t, body=body, photo=f"paid/img/{slug}.jpg", file_src=f"gh:paid/zip/{slug}.zip", file_name=f"{slug}.zip"))

# ---------------------------------------------------------------- FAYLLAR (10)
FILES = [
("Oylik_byudjet.xlsx", "Oylik oilaviy byudjet (Excel)", "Daromad va 11 ta xarajat toifasi: reja va fakt, farq qizil rangda, qoldiq, jamg'arma ulushi va xarajatlar diagrammasi avtomatik hisoblanadi.", "Sariq kataklarni to'ldirasiz, qolgani formulalar bilan o'zi chiqadi."),
("Mini_CRM.xlsx", "Mini CRM: mijozlar va sotuvlar (Excel)", "Mijozlar bazasi: manba va holat ro'yxatdan tanlanadi, «keyingi qadam» sanasi o'tib ketsa qator qizaradi. Hisobot varag'ida konversiya, o'rtacha chek va manbalar grafigi.", "300 tagacha mijoz uchun tayyor. Telefonda Excel yoki Google Sheets'da ham ishlaydi."),
("Kontent_reja_30_kun.xlsx", "30 kunlik kontent reja (Excel)", "Boshlanish sanasini yozasiz, 30 kunning sanasi va hafta kuni o'zi chiqadi. Format, mavzu, maqsad, chaqiriq va holat ustunlari, bajarilish foizi.", "Har kuni holatni «Chiqdi» qilib belgilang, rang avtomatik o'zgaradi."),
("Ombor_hisobi.xlsx", "Ombor hisobi: kirim, chiqim, qoldiq (Excel)", "Mahsulot kodi bilan kirim va chiqim yozasiz, qoldiq, ombor qiymati va holat («Yetarli», «Buyurtma bering», «Tugagan») avtomatik chiqadi.", "Do'kon, ombor va kichik ishlab chiqarish uchun."),
("Hisob_faktura.xlsx", "Hisob-faktura shabloni (Excel)", "Mahsulot, soni va narxini yozasiz: summa, jami, QQS va to'lovga summa avtomatik hisoblanadi. A4 chop etishga sozlangan.", "Rasmiy elektron hisob-faktura uchun soliq tizimi (didox va h.k.) ishlatiladi; bu tijorat hujjati namunasi."),
("Reklama_ROI_kalkulyator.xlsx", "Target reklama kalkulyatori (Excel)", "Byudjet, CPM, CTR, konversiya va o'rtacha chekni kiritasiz: lid narxi, mijoz narxi (CAC), sof foyda, ROMI va zararsizlik nuqtasi chiqadi.", "Reklamaga pul tikishdan oldin foydami yoki yo'qmi, 1 daqiqada ko'rasiz."),
("Tijorat_taklifi_shablon.docx", "Tijorat taklifi shabloni (Word)", "Mijozga yuboriladigan professional taklif: muammo, yechim, natija, narx jadvali, shartlar, «nima uchun biz» va keyingi qadam. Har bo'limda maslahat bor.", "[ ] ichini to'ldirasiz va PDF qilib yuborasiz."),
("Rezyume_shablon.docx", "Rezyume (CV) shabloni (Word)", "Zamonaviy, ish beruvchilar o'qiydigan tuzilma: qisqacha ma'lumot, natijali tajriba, ko'nikmalar jadvali, tillar va sertifikatlar.", "Har bo'limda qanday yozish maslahati bor. Tayyor bo'lgach PDF qilib saqlang."),
("Biznes_reja_shablon.docx", "Biznes reja shabloni (Word)", "10 bo'limli to'liq tuzilma: bozor, raqobatchilar jadvali, marketing, boshlang'ich xarajatlar, 3 stsenariyli moliyaviy reja, xavflar va 90 kunlik reja.", "Har bo'limdagi savollarga javob yozasiz. Bank yoki investor uchun asos."),
("AI_bilan_ishlash_30_prompt.pdf", "AI bilan ishlash: 30 ta tayyor prompt (PDF)", "Ish, marketing, sotuv, biznes, o'qish, kontent, dasturlash va shaxsiy rejalashtirish uchun 30 ta prompt. Avval yaxshi prompt yozish qoidalari.", "Promptlar asl inglizcha holida (AI ularni aniqroq tushunadi), tavsiflari o'zbekcha."),
]
for fn, t, what, tip in FILES:
    stem = fn.rsplit(".", 1)[0]
    body = (f"📄 <b>Fayl: {t}</b>\n\n{what}\n\n💡 {tip}\n🧪 Formulalar tekshirilgan, xatosiz hisoblaydi." if fn.endswith(".xlsx") else
            f"📄 <b>Fayl: {t}</b>\n\n{what}\n\n💡 {tip}") + GET + ("\n#fayl #excel" if fn.endswith(".xlsx") else "\n#fayl")
    items.append(dict(cat="file", title=t, body=body, photo=f"paid/img/file_{stem}.jpg", file_src=f"gh:paid/files/{fn}", file_name=fn))

# ---------------------------------------------------------------- APK (6, rasmiy GitHub relizlari)
APK = [
("Aegis Authenticator", "https://github.com/beemdevelopment/Aegis/releases/download/v3.4.3/aegis-v3.4.3.apk", "aegis-v3.4.3.apk", "6,9 MB", "v3.4.3",
 "Ikki bosqichli himoya (2FA) kodlari uchun: Instagram, Telegram, Google, birja va bank akkauntlaringizni o'g'irlikdan himoyalaydi. Kodlar shifrlangan, zaxira nusxa olish mumkin.",
 "https://github.com/beemdevelopment/Aegis"),
("KeePassDX: parollar menejeri", "https://github.com/Kunzisoft/KeePassDX/releases/download/4.5.8/KeePassDX-4.5.8-free.apk", "KeePassDX-4.5.8.apk", "16,8 MB", "4.5.8",
 "Barcha parollaringizni bitta shifrlangan faylda saqlaydi. Internetga ulanmaydi, reklama yo'q. Avtomatik to'ldirish va barmoq izi bilan ochish bor.",
 "https://github.com/Kunzisoft/KeePassDX"),
("LocalSend: fayllarni internetsiz uzatish", "https://github.com/localsend/localsend/releases/download/v1.18.2/LocalSend-1.18.2-android-arm64v8.apk", "LocalSend-1.18.2-arm64.apk", "46,6 MB", "1.18.2",
 "Telefon ↔ kompyuter ↔ telefon o'rtasida rasm, video va fayllarni bir xil Wi-Fi orqali tez uzatadi (AirDrop kabi). Internet trafigi sarflanmaydi, sifat pasaymaydi. Windows, Mac, iPhone versiyalari ham bor.",
 "https://github.com/localsend/localsend"),
("Fossify Gallery: reklamasiz galereya", "https://github.com/FossifyOrg/Gallery/releases/download/1.14.1/gallery-30-foss-release.apk", "Fossify-Gallery-1.14.1.apk", "38,5 MB", "1.14.1",
 "Tez va reklamasiz galereya: rasmlarni yashirish, parol bilan qulflash, oddiy tahrirlash, tiklash uchun «savat». Kuchsiz telefonlarda ham tez ishlaydi.",
 "https://github.com/FossifyOrg/Gallery"),
("Markor: eslatmalar va ro'yxatlar", "https://github.com/gsantner/markor/releases/download/v2026.10.0/net.gsantner.markor-v164-2026.10.0-flavorDefault-release.apk", "Markor-2026.10.0.apk", "11,9 MB", "2026.10.0",
 "Oddiy matnli eslatmalar, kundalik, vazifalar ro'yxati (todo.txt) va Markdown hujjatlar. Hammasi telefoningizda, reklama va kuzatuv yo'q.",
 "https://github.com/gsantner/markor"),
("Fossify File Manager: fayl menejeri", "https://github.com/FossifyOrg/File-Manager/releases/download/1.6.3/file-manager-15-foss-release.apk", "Fossify-File-Manager-1.6.3.apk", "10 MB", "1.6.3",
 "Reklamasiz, tez fayl menejeri: zip ochish, papkalarni parol bilan himoyalash, xotira tahlili, fayllarni qidirish.",
 "https://github.com/FossifyOrg/File-Manager"),
]
for name, url, fn, size, ver, what, repo in APK:
    body = (f"📲 <b>Ilova (APK): {name}</b>\n\n{what}\n\n"
            f"📦 Versiya: {ver} · Hajmi: {size}\n🔓 Bepul, ochiq kodli, reklamasiz\n🔗 Rasmiy manba: {repo}\n\n"
            "<b>O'rnatish:</b>\n1. Pastdagi tugma orqali APK'ni botdan oling.\n2. Faylni bosing → «Noma'lum manbalardan o'rnatishga ruxsat» so'ralsa, shu safar uchun ruxsat bering.\n3. «O'rnatish» ni bosing.\n"
            "🛡 Fayl dasturchining rasmiy GitHub relizidan olingan, o'zgartirilmagan." + ("\n⚠️ Bu versiya zamonaviy (arm64) telefonlar uchun." if "arm64" in fn else "") +
            GET + "\n#ilova #apk")
    items.append(dict(cat="apk", title=name, body=body, file_src=f"url:{url}", file_name=fn, check_urls=[repo]))

# ---------------------------------------------------------------- ARALASH TARTIB
order = ["prompt", "site", "apk", "file", "code", "link", "design", "n8n", "prompt", "file", "apklink", "code", "site", "apk", "prompt", "file", "design", "link", "code", "n8n"]
by = {}
for it in items: by.setdefault(it["cat"], []).append(it)
res, k = [], 0
cats_left = lambda: any(by.get(c) for c in by)
while cats_left():
    c = order[k % len(order)]; k += 1
    if c == "n8n": res.append({"cat": "n8n", "slot": True}); continue
    if by.get(c): res.append(by[c].pop(0))
    if k > 2000: break
# n8n slotlari kerakli sondan ko'p bo'lsa, ortiqchasini olib tashlaymiz (5 ta)
n8n_seen = 0; final = []
for it in res:
    if it.get("slot"):
        n8n_seen += 1
        if n8n_seen > 5: continue
    final.append(it)
for i, it in enumerate(final, 1): it["ord"] = i * 10
json.dump(final, open(f"{P}/items_all.json", "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(final), Counter(i["cat"] for i in final))
print([i["cat"] for i in final])
