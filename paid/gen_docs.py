# 3 ta Word shablon + 1 ta PDF qo'llanma
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = "/home/claude/bot/paid/files"
BLUE = RGBColor(0x1F, 0x4E, 0x78); GREY = RGBColor(0x7F, 0x7F, 0x7F)

def base(doc):
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    for s in doc.sections: s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(1.8)
    for lvl, size in ((1, 16), (2, 13)):
        h = doc.styles[f"Heading {lvl}"]; h.font.color.rgb = BLUE; h.font.size = Pt(size); h.font.name = "Calibri"

def hint(doc, text):
    p = doc.add_paragraph(); r = p.add_run(text); r.italic = True; r.font.color.rgb = GREY; r.font.size = Pt(10)

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), color); tcPr.append(sh)

def table(doc, rows, widths=None, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = str(v)
            if header and i == 0:
                shade(c, "1F4E78")
                for r in c.paragraphs[0].runs: r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
            if widths: c.width = Cm(widths[j])
    return t

# ---------------------------------------------------------------- F7 Tijorat taklifi
d = Document(); base(d)
p = d.add_paragraph(); r = p.add_run("[KOMPANIYA NOMI]"); r.bold = True; r.font.size = Pt(18); r.font.color.rgb = BLUE
d.add_paragraph("[Manzil] · [Telefon] · [Email] · [Sayt / Telegram]").runs[0].font.color.rgb = GREY
d.add_paragraph("_" * 90)
p = d.add_paragraph(); p.add_run("Kimga: ").bold = True; p.add_run("[Mijoz kompaniya nomi, rahbar F.I.O.]")
p = d.add_paragraph(); p.add_run("Sana: ").bold = True; p.add_run("[__.__.2026]     "); p.add_run("№ ").bold = True; p.add_run("[TT-001]")
d.add_heading("TIJORAT TAKLIFI: [xizmat/mahsulot nomi]", 1)
hint(d, "Maslahat: sarlavhada mijoz oladigan natijani yozing. Masalan: «Sotuvlarni 30 kunda oshirish uchun Telegram bot».")
d.add_paragraph("Hurmatli [Ism Sharif]!")
d.add_paragraph("[1-2 gap: mijozning vaziyati va muammosi. Masalan: Siz bilan [sana]dagi suhbatda buyurtmalar qo'lda qabul qilinishi va ba'zi mijozlar javobsiz qolayotgani haqida gaplashdik.]")
d.add_heading("Biz taklif qilamiz", 2)
for x in ["[Yechim 1: nima qilinadi va mijozga foydasi]", "[Yechim 2]", "[Yechim 3]"]: d.add_paragraph(x, style="List Bullet")
d.add_heading("Siz nimaga erishasiz", 2)
for x in ["[Natija 1: raqam bilan, agar aniq bo'lsa. Masalan: buyurtma qabul qilish vaqti 2 baravar qisqaradi]", "[Natija 2]", "[Natija 3]"]: d.add_paragraph(x, style="List Bullet")
d.add_heading("Narx va shartlar", 2)
table(d, [["№", "Xizmat / mahsulot", "Soni", "Narxi (so'm)", "Summa (so'm)"],
          ["1", "[...]", "1", "[...]", "[...]"], ["2", "[...]", "1", "[...]", "[...]"], ["3", "[...]", "1", "[...]", "[...]"],
          ["", "", "", "Jami:", "[...]"]], [1, 7.5, 1.6, 3.2, 3.4])
d.add_paragraph()
for k, v in [("Bajarish muddati:", "[__ ish kuni]"), ("To'lov tartibi:", "[50% oldindan, 50% topshirilganda]"), ("Kafolat:", "[__ oy bepul texnik yordam]"), ("Taklif amal qilish muddati:", "[__.__.2026 gacha]")]:
    p = d.add_paragraph(); p.add_run(k + " ").bold = True; p.add_run(v)
d.add_heading("Nima uchun biz", 2)
for x in ["[Tajriba: necha yil, nechta loyiha]", "[Haqiqiy mijozlar yoki loyihalar (ruxsat bilan)]", "[Ajralib turadigan jihat]"]: d.add_paragraph(x, style="List Bullet")
d.add_heading("Keyingi qadam", 2)
d.add_paragraph("[Aniq chaqiriq: Masalan, «Shu hafta 20 daqiqalik onlayn uchrashuvda tafsilotlarni kelishib olaylik. Qulay vaqtingizni yozing.»]")
d.add_paragraph("\nHurmat bilan,\n[F.I.O.], [lavozim]\n[Telefon]")
d.save(f"{OUT}/Tijorat_taklifi_shablon.docx")

# ---------------------------------------------------------------- F8 Rezyume
d = Document(); base(d)
p = d.add_paragraph(); r = p.add_run("[ISM FAMILIYA]"); r.bold = True; r.font.size = Pt(24); r.font.color.rgb = BLUE
p = d.add_paragraph(); r = p.add_run("[Lavozim: masalan, SMM mutaxassisi / Frontend dasturchi]"); r.font.size = Pt(13); r.font.color.rgb = GREY
d.add_paragraph("📞 [+998 __ ___ __ __]   ✉ [email]   ✈ [t.me/username]   📍 [Shahar]   🔗 [LinkedIn / portfolio]")
d.add_heading("Qisqacha men haqimda", 2)
hint(d, "2-3 gap: kim ekaningiz, necha yil tajriba, eng kuchli natijangiz. «Mas'uliyatli, kirishimli» kabi umumiy so'zlar o'rniga fakt yozing.")
d.add_paragraph("[Masalan: 3 yillik tajribaga ega SMM mutaxassisi. 12 ta kichik biznes sahifasini yuritib, obunachilarni o'rtacha 2,5 baravar oshirganman. Kontent rejalashtirish va target reklamada kuchliman.]")
d.add_heading("Ish tajribasi", 2)
for _ in range(2):
    p = d.add_paragraph(); p.add_run("[Lavozim] · [Kompaniya]").bold = True; p.add_run("    [oy.yil – oy.yil / hozir]").font.color.rgb = GREY
    for x in ["[Natija bilan yozing: Nima qildingiz → qanday natija. Masalan: Instagram sahifani 2 000 dan 9 000 obunachiga yetkazdim]", "[Yana bir natija]", "[Mas'uliyat yoki loyiha]"]:
        d.add_paragraph(x, style="List Bullet")
d.add_heading("Ta'lim", 2)
p = d.add_paragraph(); p.add_run("[Universitet / o'quv markazi], [yo'nalish]").bold = True; p.add_run("    [yil – yil]").font.color.rgb = GREY
d.add_heading("Ko'nikmalar", 2)
table(d, [["Professional", "Dasturlar", "Shaxsiy"], ["[Kontent reja]", "[Canva, Figma]", "[Muzokara]"], ["[Target reklama]", "[Meta Ads Manager]", "[Vaqtni boshqarish]"], ["[Kopirayting]", "[Excel / Sheets]", "[Jamoada ishlash]"]], [5.5, 5.5, 5.5])
d.add_heading("Tillar", 2)
d.add_paragraph("O'zbek: ona tili · Rus: [daraja] · Ingliz: [daraja, masalan B2 / IELTS 6.5]")
d.add_heading("Sertifikatlar va qo'shimcha", 2)
d.add_paragraph("[Kurs nomi, tashkilot, yil]", style="List Bullet"); d.add_paragraph("[Portfolio / loyiha havolasi]", style="List Bullet")
hint(d, "Yuborishdan oldin: [ ] ichidagi hamma joyni to'ldiring, kerak bo'lmagan bo'limni o'chiring, faylni PDF qilib saqlang (Fayl → Saqlash → PDF).")
d.save(f"{OUT}/Rezyume_shablon.docx")

# ---------------------------------------------------------------- F9 Biznes reja
d = Document(); base(d)
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; r = p.add_run("BIZNES REJA"); r.bold = True; r.font.size = Pt(28); r.font.color.rgb = BLUE
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run("[Loyiha nomi]\n[Tadbirkor F.I.O.] · [Shahar] · [2026]").font.size = Pt(13)
hint(d, "Har bo'limda kursivdagi savollarga javob yozing, keyin savollarni o'chiring. Bank yoki investor uchun raqamlarni haqiqiy manbalardan oling.")
secs = [
 ("1. Qisqacha mazmun (rezyume)", ["Nima sotasiz va kimga?", "Qancha mablag' kerak va nimaga sarflanadi?", "Qachon o'zini oqlaydi (oy)?", "Bu bo'limni eng oxirida yozing, 1 sahifadan oshmasin."]),
 ("2. Mahsulot yoki xizmat", ["Mijozning qaysi muammosini hal qiladi?", "Raqobatchilardan nimasi bilan farq qiladi?", "Narxi va tannarxi qancha?"]),
 ("3. Bozor va mijozlar", ["Ideal mijozingiz kim (yosh, joy, daromad, odatlar)?", "Hududda bunday mijozlar taxminan nechta?", "Ular hozir muammoni qanday hal qilyapti?"]),
 ("4. Raqobatchilar", ["3-5 asosiy raqobatchi: narxi, kuchli va zaif tomoni (jadvalga yozing)."]),
 ("5. Marketing va sotuv", ["Birinchi 100 mijozni qayerdan va qanday topasiz?", "Qaysi kanallar: Instagram, Telegram, marketpleys, tavsiya, offline?", "Oylik marketing byudjeti va bitta mijoz narxi (CAC)?"]),
 ("6. Ishlab chiqarish / faoliyat jarayoni", ["Joy, uskuna, yetkazib beruvchilar.", "Bir kunlik ish jarayoni qanday?"]),
 ("7. Jamoa", ["Kimlar kerak, vazifalari va oylik maoshi.", "Sizning tajribangiz."]),
 ("8. Moliyaviy reja", ["Boshlang'ich xarajatlar ro'yxati (pastdagi jadval).", "Oylik doimiy xarajatlar.", "3 ta stsenariy: yomon / o'rtacha / yaxshi: oylik tushum va foyda.", "Zararsizlik nuqtasi: oyiga nechta sotuv kerak?"]),
 ("9. Xavflar va ularni kamaytirish", ["Eng katta 5 ta xavf va har biriga reja."]),
 ("10. Ishga tushirish rejasi", ["Haftama-hafta: birinchi 90 kun."]),
]
for t, qs in secs:
    d.add_heading(t, 1)
    for q in qs: hint(d, "• " + q)
    d.add_paragraph("[Javobingiz]")
    if t.startswith("4."):
        table(d, [["Raqobatchi", "Narx", "Kuchli tomoni", "Zaif tomoni"], ["[...]", "[...]", "[...]", "[...]"], ["[...]", "[...]", "[...]", "[...]"], ["[...]", "[...]", "[...]", "[...]"]], [4, 3, 5, 5])
    if t.startswith("8."):
        d.add_paragraph()
        table(d, [["Boshlang'ich xarajat", "Summa (so'm)"], ["Ijara (birinchi oylar)", "[...]"], ["Uskuna va jihozlar", "[...]"], ["Ta'mir / bezak", "[...]"], ["Birinchi tovar zaxirasi", "[...]"], ["Ruxsatnomalar, ro'yxatdan o'tish", "[...]"], ["Marketing (ishga tushirish)", "[...]"], ["Zaxira (kutilmagan xarajatlar, 10-15%)", "[...]"], ["JAMI", "[...]"]], [10, 5])
        d.add_paragraph()
        table(d, [["Ko'rsatkich (oylik)", "Yomon", "O'rtacha", "Yaxshi"], ["Sotuvlar soni", "", "", ""], ["Tushum", "", "", ""], ["Tannarx", "", "", ""], ["Doimiy xarajatlar", "", "", ""], ["Sof foyda", "", "", ""]], [6, 3.5, 3.5, 3.5])
    if t.startswith("10."):
        table(d, [["Muddat", "Vazifa", "Mas'ul", "Natija"], ["1-2 hafta", "[...]", "[...]", "[...]"], ["3-4 hafta", "[...]", "[...]", "[...]"], ["2-oy", "[...]", "[...]", "[...]"], ["3-oy", "[...]", "[...]", "[...]"]], [3, 7, 3, 4])
d.save(f"{OUT}/Biznes_reja_shablon.docx")
print("docx ok")

# ---------------------------------------------------------------- F10 PDF: AI bilan ishlash qo'llanmasi + 30 prompt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape as X
D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("U", D + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("U-B", D + "DejaVuSans-Bold.ttf")); pdfmetrics.registerFont(TTFont("M", D + "DejaVuSansMono.ttf"))
addMapping("U", 0, 0, "U"); addMapping("U", 1, 0, "U-B")
N = ParagraphStyle("n", fontName="U", fontSize=10, leading=14.5)
T = ParagraphStyle("t", fontName="U-B", fontSize=26, leading=32, alignment=TA_CENTER, textColor=colors.HexColor("#1F4E78"))
H1 = ParagraphStyle("h1", fontName="U-B", fontSize=15, leading=20, textColor=colors.HexColor("#1F4E78"), spaceBefore=10, spaceAfter=6)
H2 = ParagraphStyle("h2", fontName="U-B", fontSize=11.5, leading=15, spaceBefore=6, spaceAfter=3)
CODE = ParagraphStyle("c", fontName="M", fontSize=8.6, leading=12, textColor=colors.HexColor("#0f172a"))
G = [
 ("Ish va karyera", [
  ("Rezyumeni vakansiyaga moslash", "Rezyume va vakansiya matnini solishtirib, kalit so'zlar va yaxshilangan bandlarni beradi.", "Act as a senior recruiter. Compare my resume with this job description. List missing keywords, rewrite my 5 weakest bullet points with measurable results, and suggest a 3-sentence summary tailored to this role.\nResume: [paste]\nJob description: [paste]\nReply in Uzbek (Latin script)."),
  ("Suhbatga tayyorgarlik", "Lavozim bo'yicha ehtimoliy savollar va STAR usulida namunaviy javoblar.", "You are an interviewer for the role of [role] at a [industry] company. Ask me 10 likely interview questions one by one. After each of my answers, score it 1-10 and show a better answer using the STAR method. Reply in Uzbek (Latin script)."),
  ("Ish xati (cover letter)", "Qisqa, aniq va shaxsiy motivatsion xat.", "Write a 180-word cover letter for [role] at [company]. My top 3 achievements: [list]. Why this company: [reason]. Tone: confident, warm, no clichés. Reply in Uzbek (Latin script)."),
 ]),
 ("Marketing va SMM", [
  ("30 kunlik kontent reja", "Mavzu, format va chaqiriqlar bilan to'liq oylik reja.", "Create a 30-day content plan for [business] on [platform] for [audience]. Table columns: day, format (Reels/Carousel/Stories/Post), topic, hook, CTA. Mix: 40% useful, 30% trust, 20% engagement, 10% sales. Reply in Uzbek (Latin script)."),
  ("Reklama matni (3 variant)", "Target reklama uchun turli yondashuvdagi matnlar.", "Write 3 ad variations for [product] targeting [audience]: 1) pain-based, 2) benefit-based, 3) social-proof-based (no invented reviews). Each: headline (40 chars), primary text (125 chars), CTA. Reply in Uzbek (Latin script)."),
  ("Izohlarga javob", "Salbiy va ijobiy izohlarga xushmuomala javoblar.", "You manage social media for [business]. Write polite replies to these comments. For negative ones: acknowledge, apologize if needed, offer a solution, move to DM. Max 2 sentences each.\nComments: [paste]\nReply in Uzbek (Latin script)."),
  ("Raqobatchi tahlili", "Raqobatchi sahifasi yoki saytidan o'rganish va ustunlik topish.", "Analyze my competitor based on this information: [paste their bio, prices, top posts or website text]. Identify their positioning, strengths, weaknesses, content patterns and gaps I can use. End with 5 concrete actions for my business [describe]. Reply in Uzbek (Latin script)."),
  ("Heshteg va kalit so'zlar", "Post uchun mos heshteglar va qidiruv so'zlari.", "Give me 20 hashtags for a post about [topic] for [city/country] audience: 5 broad, 10 niche, 5 local. Also 10 search keywords people type. Reply in Uzbek (Latin script)."),
 ]),
 ("Sotuv va mijozlar", [
  ("E'tirozlarga javob", "«Qimmat», «o'ylab ko'raman» kabi e'tirozlarga tayyor javoblar.", "List the 8 most common objections for [product] at [price] and give a short, honest answer for each (no pressure tactics). Add one follow-up question per objection. Reply in Uzbek (Latin script)."),
  ("Sotuv skripti (telefon)", "Qo'ng'iroq uchun qadamma-qadam ssenariy.", "Write a phone sales script for [product] to [customer type]: greeting, permission to talk, 3 discovery questions, short pitch, handling 3 objections, closing with a clear next step. Reply in Uzbek (Latin script)."),
  ("Mijozlar so'rovnomasi", "Mijoz fikrini bilish uchun to'g'ri savollar.", "Create a 7-question customer feedback survey for [business]. Mix: 2 rating questions, 3 multiple-choice, 2 open questions. Goal: understand why people buy, what stops them, and what to improve. Keep it under 2 minutes. Reply in Uzbek (Latin script)."),
  ("Mijozni qaytarish xabari", "Uzoq vaqt kelmagan mijozlarga yumshoq xabar.", "Write 3 short win-back messages for customers who haven't bought from [business] in [N] months. Include a reason to return (new product/useful tip/small offer). Max 300 characters each. Reply in Uzbek (Latin script)."),
 ]),
 ("Biznes va boshqaruv", [
  ("SWOT tahlil", "Biznesingizning kuchli/zaif tomonlari, imkoniyat va xavflari.", "Do a SWOT analysis for [business] in [city]. For each quadrant give 4 specific points, then 3 strategic actions that use strengths to capture opportunities. Reply in Uzbek (Latin script)."),
  ("Narx belgilash", "Tannarx va raqobatchilarga qarab narx strategiyasi.", "Help me price [product]. Cost per unit: [cost]. Competitor prices: [list]. Target customer: [who]. Suggest 3 pricing options (budget/standard/premium) with pros and cons, and a simple bundle offer. Reply in Uzbek (Latin script)."),
  ("Xodim uchun yo'riqnoma (SOP)", "Takrorlanadigan ishni hujjatlashtirish.", "Write a step-by-step SOP for [task, e.g., processing an online order] for a new employee. Include: goal, tools, steps with checkboxes, common mistakes, quality check. Reply in Uzbek (Latin script)."),
  ("Vakansiya e'loni", "Jalb qiluvchi va aniq ish e'loni.", "Write a job post for [role] at [company]: about us (2 lines), responsibilities (5), requirements (5), what we offer (5), salary range [range], how to apply. Reply in Uzbek (Latin script)."),
 ]),
 ("O'qish va rivojlanish", [
  ("Murakkab mavzuni oddiy tushuntirish", "Istalgan mavzuni 12 yoshli bola tushunadigan qilib.", "Explain [topic] as if I were 12. Then give one real-life example, one common misconception, and 3 quiz questions to check my understanding. Reply in Uzbek (Latin script)."),
  ("Kitob xulosasi", "Kitobdan asosiy g'oyalar va amaliy qadamlar.", "Summarize the key ideas of the book [title] by [author] in 10 bullet points, then give 5 practical actions I can take this week. If you are not sure about details, say so. Reply in Uzbek (Latin script)."),
  ("Test savollari tuzish", "Mavzu bo'yicha javoblari bilan test.", "Create 15 multiple-choice questions on [topic] for [level] learners. 4 options each, mark the correct answer with *, mix easy/medium/hard, and add a one-line explanation for each answer. Reply in Uzbek (Latin script)."),
  ("Til o'rganish suhbatdoshi", "Ingliz tilida suhbat, xatolarni tuzatish bilan.", "Let's practice English conversation about [topic]. Keep your messages short. After each of my replies, correct my mistakes in a short list, then continue the conversation. My level: [A2/B1/B2]."),
 ]),
 ("Kontent va matn", [
  ("Matnni tahrirlash", "Grammatika, uslub va qisqartirish.", "Edit the text below: fix grammar and spelling, make it clearer and 20% shorter, keep my voice. Show the final text, then a short list of the main changes.\nText: [paste]\nReply in Uzbek (Latin script)."),
  ("Maqola rejasi", "SEO uchun tuzilgan maqola rejasi.", "Create an outline for a blog article about [topic] for [audience]: SEO title, meta description, H2/H3 structure, key points per section, FAQ (5 questions). Reply in Uzbek (Latin script)."),
  ("Telegram post", "Kanal uchun o'qiladigan qisqa post.", "Write a Telegram channel post about [topic] (600-900 characters): hook in the first line, 3 short paragraphs or a list, one emoji per paragraph max, a question at the end to drive comments. Reply in Uzbek (Latin script)."),
  ("YouTube video ssenariysi", "8-10 daqiqalik video uchun tuzilma.", "Write a script outline for a [length]-minute YouTube video about [topic]: hook (first 15 seconds), intro, 5 main sections with talking points, B-roll ideas, CTA, title and thumbnail text options (3 each). Reply in Uzbek (Latin script)."),
 ]),
 ("Dasturlash va avtomatlashtirish", [
  ("Kod yozish (aniq talab bilan)", "Toza, izohli kod va ishga tushirish yo'riqnomasi.", "Write a [language] script that [task]. Requirements: [list]. Include error handling, comments in English, and instructions to run it. Then explain the code briefly in Uzbek (Latin script)."),
  ("n8n avtomatlashtirish g'oyasi", "Biznes jarayonini avtomatlashtirish rejasi.", "I run [business]. Suggest 5 automations I can build with n8n (or Make). For each: trigger, steps (nodes), apps needed, time saved per week. Then describe the first one step by step. Reply in Uzbek (Latin script)."),
  ("SQL so'rov", "Ma'lumotlar bazasidan kerakli hisobot.", "Write a SQL query for [PostgreSQL/MySQL]. Tables: [describe tables and columns]. I need: [report]. Explain each part of the query. Reply in Uzbek (Latin script)."),
 ]),
 ("Shaxsiy", [
  ("Haftalik reja", "Maqsadlarni kunlarga bo'lingan aniq rejaga aylantirish.", "Help me plan my week. My goals: [list]. Fixed commitments: [list]. Energy: I work best at [time]. Create a day-by-day plan with time blocks, 3 priorities per day, and buffer time. Reply in Uzbek (Latin script)."),
  ("Xarajatlarni kamaytirish", "Oylik xarajatlardan tejash imkoniyatlari.", "Here are my monthly expenses: [list categories and amounts]. Monthly income: [amount]. Find 5 realistic ways to save 10-20% without hurting quality of life, estimate savings for each, and suggest a simple 50/30/20-style budget for me. Reply in Uzbek (Latin script)."),
  ("Sayohat rejasi", "Kunlik marshrut va byudjet.", "Plan a [N]-day trip to [city] for [people] with a budget of [amount]. Day-by-day itinerary, transport tips, food suggestions, estimated costs. Mark anything that should be double-checked (prices, opening hours). Reply in Uzbek (Latin script)."),
 ]),
]
doc = SimpleDocTemplate(f"{OUT}/AI_bilan_ishlash_30_prompt.pdf", pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                        title="AI bilan ishlash: 30 ta tayyor prompt", author="AI PromptMaster")
E = [Spacer(1, 50 * mm), Paragraph("AI bilan ishlash", T), Paragraph("30 ta tayyor prompt", T), Spacer(1, 10 * mm),
     Paragraph("ChatGPT, Claude va Gemini uchun ish, marketing, sotuv, o'qish va dasturlashga oid tayyor so'rovlar. Har biri: nima qiladi va nusxa olinadigan prompt.", ParagraphStyle("x", parent=N, alignment=TA_CENTER, fontSize=12, leading=18)),
     Spacer(1, 70 * mm), Paragraph("AI PromptMaster · 2026", ParagraphStyle("y", parent=N, alignment=TA_CENTER, textColor=colors.grey)), PageBreak()]
E += [Paragraph("Yaxshi prompt qanday yoziladi", H1)]
for k, v in [("1. Rol bering.", "«Sen tajribali marketologsan» deb boshlash javob sifatini oshiradi."), ("2. Kontekst bering.", "Biznesingiz, mijozingiz, narx, shahar: qancha aniq bo'lsa, javob shuncha foydali."),
             ("3. Natija formatini ayting.", "Jadval, ro'yxat, 3 variant, 500 belgigacha va h.k."), ("4. Cheklov qo'ying.", "«Yolg'on raqam yozma», «bosimsiz», «oddiy tilda»."),
             ("5. Davom ettiring.", "Birinchi javob ideal bo'lmasa: «qisqaroq qil», «2-variantni rivojlantir» deb so'rang."),
             ("6. Tekshiring.", "AI xato qilishi mumkin: raqamlar, faktlar, qonunlar va narxlarni rasmiy manbadan tekshiring.")]:
    E.append(Paragraph(f"<b>{k}</b> {v}", N)); E.append(Spacer(1, 2 * mm))
E.append(Spacer(1, 3 * mm)); E.append(Paragraph("Promptlar inglizcha qoldirilgan: AI inglizcha ko'rsatmani aniqroq tushunadi. Oxiridagi «Reply in Uzbek (Latin script)» qatori javobni o'zbekcha qiladi. [ ] ichini o'zingiznikiga almashtiring (o'zbekcha yozsangiz ham bo'ladi).", N))
n = 0
for cat, items in G:
    E.append(Paragraph(cat, H1))
    for name, what, prompt in items:
        n += 1
        box = Table([[Paragraph(X(prompt).replace("\n", "<br/>"), CODE)]], colWidths=[174 * mm])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        E.append(KeepTogether([Paragraph(f"{n}. {name}", H2), Paragraph(what, N), Spacer(1, 2 * mm), box, Spacer(1, 3 * mm)]))
assert n == 30, n
def footer(c, d):
    c.saveState(); c.setFont("U", 8); c.setFillColor(colors.grey); c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{d.page}"); c.drawString(18 * mm, 10 * mm, "AI PromptMaster: faqat shaxsiy foydalanish uchun"); c.restoreState()
doc.build(E, onLaterPages=footer)
print("pdf ok", n)
