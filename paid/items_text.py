# Matnli postlar: 10 prompt, 5 foydali sayt, 4 rasmiy AI ilova.
import json, html

def pre(t):  # Telegram HTML uchun xavfsiz <pre>
    return "<pre>" + html.escape(t.strip(), quote=False) + "</pre>"

FOOT_P = ("\n\n✏️ <b>Ishlatish:</b> prompt ustiga bosing (nusxa olinadi), [ ] ichini o'zingiznikiga almashtiring, ChatGPT, Claude yoki Gemini'ga yuboring. "
          "[ ] ichini o'zbekcha yozsangiz ham bo'ladi. Oxiridagi «Reply in Uzbek» qatori javobni o'zbekcha qiladi.\n#prompt")

P = [
("Biznes g'oyani 10 daqiqada tekshirish",
 "G'oyangizni talab, raqobat, foyda, xarajat bo'yicha baholaydi, 5 ta asosiy xavfni va ularni 7 kunda arzon sinash yo'lini, 14 kunda ishga tushadigan kichik versiyani va oddiy hisob-kitobni beradi. Oxirida aniq xulosa: boshlash, o'zgartirish yoki to'xtatish.",
 """You are a pragmatic startup advisor who has evaluated 500+ small businesses in Central Asia.

My idea: [describe your business idea in 2-3 sentences]
City/market: [e.g., Tashkent]
Budget: [e.g., $2,000]
My skills: [e.g., sales, design, no coding]
Target monthly income: [e.g., $1,000]

Do the following:
1. Restate the idea in one sentence: the exact customer and their pain.
2. Score it 1-10 on demand, competition, profit margin, startup cost and my fit. One line of reasoning per score.
3. List the 5 biggest risks and how to test each one in under 7 days for under $50.
4. Design a minimum version I can launch in 14 days: what to sell, the price, where to find the first 10 customers.
5. Unit economics table: price, cost per unit, margin, customers needed per month to reach my target income.
6. Verdict: GO / CHANGE / STOP, plus the single most important next step.

Be honest and specific. If information is missing, state your assumptions.
Reply in Uzbek (Latin script)."""),
("Reels/TikTok uchun 3 xil ssenariy",
 "Mavzuingiz bo'yicha 3 xil qisqa video ssenariysini yozadi: birinchi 2 soniyadagi «ilmoq», sahna-sahna jadval (nima ko'rinadi, nima aytiladi, ekrandagi yozuv), tomoshabinni ushlab turadigan burilish nuqtasi, chaqiriq, izoh matni va heshteglar.",
 """Act as a short-form video strategist who writes high-retention Instagram Reels and TikTok scripts.

Topic: [your topic or product]
Audience: [who watches: age, interests]
Goal: [followers / sales / DMs]
Length: [15 / 30 / 60] seconds

Write 3 different script options. For each one:
- Hook (first 2 seconds): one spoken line that stops the scroll + the on-screen text.
- Scene-by-scene table: time | what we see | what is said | on-screen text.
- One pattern-interrupt moment to keep people watching.
- A call to action that matches the goal.
- Caption (max 300 characters) and 5 relevant hashtags.

Rules: simple spoken language, no clichés like "In today's video", every line must earn its place, nothing that cannot be filmed with a phone.
Reply in Uzbek (Latin script)."""),
("Ideal mijoz portreti (persona)",
 "Mahsulotingizni kim, nima uchun va qanday holatda sotib olishini aniqlaydi: 3 ta mijoz turi, ularning og'riqlari, e'tirozlari, qayerda vaqt o'tkazishi va har biriga mos reklama gaplari. Reklama sozlash va post yozishdan oldin juda foydali.",
 """You are a senior marketing researcher.

Product/service: [what you sell]
Price: [price]
Where I sell: [Instagram / Telegram / shop / marketplace]
What I know about my current customers: [anything you know]

Create 3 distinct customer personas. For each persona give:
1. Name, age, job, income level, city type.
2. The moment they start looking for a product like mine (trigger situation).
3. Top 3 pains and top 3 desired outcomes, in their own words.
4. Top 3 objections before buying and the best honest answer to each.
5. Where they spend time online and offline; which content formats they trust.
6. 3 ad headlines and 1 short ad text written specifically for them.

Finish with: which persona to target first and why, and 3 questions I should ask real customers to verify these personas.
Reply in Uzbek (Latin script)."""),
("Sotadigan sayt (landing) matni",
 "Mahsulot yoki xizmatingiz uchun bir sahifali saytning to'liq matnini yozadi: sarlavha, muammo, yechim, foydalar, ishonch bloki, savol-javob, chaqiriq tugmalari. 2 xil variant beradi: biri qisqa, biri batafsil.",
 """You are a conversion copywriter. Write landing page copy for:

Offer: [product/service]
Customer: [who it is for]
Main result the customer gets: [result]
Price and terms: [price, delivery, guarantee if any]
Proof I have: [reviews, numbers, experience; write "none" if none]

Deliver two versions:
A) Short page (for mobile ads)
B) Long page (for warm traffic)

Each version must include: headline + subheadline, problem section, solution, 5 benefits (outcome-focused, not features), how it works in 3 steps, trust section, FAQ with 6 real objections, and 3 call-to-action button texts.

Rules: no fake reviews, no invented numbers, no exaggerated promises. If I gave no proof, suggest what proof I could collect.
Reply in Uzbek (Latin script)."""),
("Har qanday mavzuni tez o'rganish (shaxsiy ustoz)",
 "AI'ni shaxsiy ustozga aylantiradi: darajangizni aniqlaydi, 14 kunlik reja tuzadi, har mavzuni oddiy misol bilan tushuntiradi va savollar bilan tekshiradi. Dasturlash, til, marketing, matematika, istalgan narsa uchun.",
 """Be my personal tutor for: [topic, e.g., Excel / Python / English grammar / digital marketing]
My current level: [beginner / intermediate]
Time per day: [e.g., 40 minutes]
My goal in 14 days: [concrete goal]

Process:
1. First ask me 5 short diagnostic questions to check my real level. Wait for my answers.
2. Then build a 14-day plan: daily topic, 20-minute explanation, 15-minute practice task, 5-minute self-check.
3. When I say "start day N", teach that day: explain simply with an everyday analogy, give one worked example, then give me a practice task and wait for my answer.
4. Check my answer, point out mistakes kindly, and give one harder follow-up.
5. Every 3 days give a short mixed quiz on previous days.

Never give the answer to a practice task before I try. Keep explanations short.
Reply in Uzbek (Latin script)."""),
("Kod xatosini topish va tuzatish",
 "Ishlamayotgan kodingizni tajribali dasturchi kabi ko'rib chiqadi: xato sababini, tuzatilgan kodni, nima uchun shunday ekanini tushuntiradi va kelajakda shu xato qaytarilmasligi uchun maslahat beradi. Python, JavaScript, PHP va boshqa tillar uchun.",
 """You are a senior software engineer and patient mentor.

Language/framework: [e.g., Python 3.12, aiogram 3 / JavaScript, React]
What the code should do: [expected behavior]
What happens instead: [actual behavior]
Error message (full): [paste error or write "no error"]
Code:
[paste your code here]

Please:
1. Explain the root cause in 2-3 simple sentences.
2. Give the corrected code (full function or file, not fragments), with comments only where something changed.
3. Explain why the fix works.
4. Point out any other bugs, security issues or bad practices you see, ranked by importance.
5. Suggest one small test I can run to confirm it works.

If something is unclear, ask me before guessing.
Reply in Uzbek (Latin script), but keep the code and code comments in English."""),
("Excel va Google Sheets formulalari ustasi",
 "Jadval bilan ishlaganda kerakli formulani yozib beradi va qadamma-qadam tushuntiradi: VLOOKUP/XLOOKUP, SUMIFS, sana bilan ishlash, takrorlarni topish, avtomatik hisobotlar. Xato chiqqan formulani ham tuzatadi.",
 """You are an Excel and Google Sheets expert.

Program: [Excel 365 / Excel 2016 / Google Sheets]
My table: [describe columns, e.g., A: date, B: product, C: quantity, D: price; data in rows 2-500]
What I want: [e.g., total sales per product per month / find duplicates / auto status if overdue]

Give me:
1. The exact formula ready to paste (tell me which cell to put it in).
2. A step-by-step explanation of each part of the formula.
3. An alternative formula for older Excel versions if needed.
4. Common mistakes that cause errors (#N/A, #VALUE!) with this formula and how to fix them.
5. If a pivot table, conditional formatting or a chart would be better, explain how to do it in 5 steps.

Use comma or semicolon separators as appropriate and tell me which one my program likely needs.
Reply in Uzbek (Latin script)."""),
("Mijozga birinchi xabar (Telegram/email) ketma-ketligi",
 "Begona mijozga yoziladigan birinchi xabar va keyingi 3 ta eslatma xabarini yozadi: qisqa, shaxsiy, bosimsiz. Hamkorlik, B2B sotuv, bloger bilan kelishish, ish izlash uchun ishlaydi.",
 """You are an expert in B2B outreach and polite, non-pushy sales.

Who I am: [name, what I do]
Who I am writing to: [role/type of person or company]
What I offer: [offer]
Why it is relevant to them: [specific reason]
Channel: [Telegram / email / Instagram DM]

Write a 4-message sequence:
1. First message (max 450 characters): personal opening, one clear value, a low-commitment question.
2. Follow-up after 2 days: add a useful insight or example, no guilt-tripping.
3. Follow-up after 5 days: short case or idea specific to them.
4. Final polite close after 10 days that keeps the door open.

For each message give 2 subject line or opening line options. No fake familiarity, no exaggerated claims.
Reply in Uzbek (Latin script)."""),
("Marketpleys (Uzum, Wildberries) uchun mahsulot kartochkasi",
 "Mahsulotingiz uchun qidiruvda chiqadigan sarlavha, kalit so'zlar, xususiyatlar ro'yxati va xaridorni ishontiradigan tavsif yozadi. Rasmlar uchun 6 ta slayd g'oyasini ham beradi.",
 """You are an e-commerce SEO specialist for marketplaces like Uzum Market, Wildberries and Ozon.

Product: [name, brand, model]
Key specs: [size, material, color, etc.]
Who buys it and why: [customer and use case]
Price segment: [budget / mid / premium]
Competitor advantages I know: [optional]

Create:
1. 3 product title options (max 100 characters) with the main search keywords first.
2. 15 search keywords and phrases buyers actually type, in Uzbek and Russian.
3. A characteristics list in "parameter: value" format.
4. A product description (900-1200 characters): benefits first, then specs, then care/usage, then what is in the box.
5. 6 image slide ideas (what to show, short text on each slide).
6. 5 answers to typical buyer questions.

No false claims or invented certificates.
Reply in Uzbek (Latin script); give the Russian keywords in Russian."""),
("Uchrashuv yoki ovozli xabardan aniq xulosa",
 "Uzun uchrashuv yozuvi, ovozli xabar matni yoki chatni tartibli xulosaga aylantiradi: asosiy qarorlar, kim nima qiladi va qachongacha, ochiq savollar. Natijani jamoaga yuboriladigan qisqa xabar ko'rinishida ham beradi.",
 """You are an executive assistant. Below is a raw transcript/notes of a meeting or voice message.

Context: [what the meeting was about, who attended]
Transcript:
[paste text here]

Produce:
1. TL;DR in 3 sentences.
2. Key decisions made (bullet list).
3. Action items table: task | owner | deadline | priority. If owner or deadline is missing, mark it "not assigned".
4. Open questions and risks that need follow-up.
5. A short message I can send to the team in Telegram summarizing the above (max 700 characters).

Do not add information that is not in the transcript.
Reply in Uzbek (Latin script)."""),
]

L = [  # foydali saytlar
("Google AI Studio: Gemini'ning eng kuchli modellari bepul", "https://aistudio.google.com",
 "Google'ning rasmiy sayti. Gemini'ning eng yangi modellari bilan bepul ishlash, uzun PDF va videolarni tahlil qilish, rasm yaratish, hamda o'z dasturingiz uchun bepul API kalit olish mumkin.",
 ["Google akkaunt bilan kiring.", "Chapdagi «Chat» bo'limida savol yozing yoki fayl yuklang (PDF, rasm, video).", "O'ng tomonda modelni tanlang; kod yozadiganlar uchun «Get API key» tugmasi bor."],
 "n8n, bot yoki sayt uchun bepul AI kerak bo'lsa, API kalitni shu yerdan olasiz."),
("NotebookLM: hujjatlaringizdan shaxsiy AI yordamchi", "https://notebooklm.google.com",
 "Google'ning bepul vositasi. PDF, Word, sayt havolasi yoki YouTube videoni yuklaysiz, u faqat shu manbalar asosida javob beradi, xulosa, test savollari va hatto audio-podkast tayyorlaydi.",
 ["Google akkaunt bilan kiring, «New notebook» ni bosing.", "Kitob, ma'ruza, shartnoma yoki video havolasini qo'shing.", "Savol bering yoki «Audio Overview» bilan audio xulosa yarating."],
 "O'qish, imtihonga tayyorlanish va katta hujjatlarni tez tushunish uchun eng yaxshi vositalardan biri."),
("Gamma: taqdimotni 1 daqiqada yaratish", "https://gamma.app",
 "Mavzuni yozasiz, AI tayyor dizaynli taqdimot, hujjat yoki bir sahifali sayt yaratadi. Matn va rasmlarni keyin o'zingiz tahrirlaysiz, PDF yoki PowerPoint qilib yuklab olasiz.",
 ["Ro'yxatdan o'ting (bepul limit bor).", "«Create new» → «Generate» → mavzu va slaydlar sonini yozing.", "Tayyor bo'lgach, matnni tahrirlang va «Export» orqali PDF/PPTX yuklang."],
 "Mijozga taklif, o'quv taqdimoti yoki biznes reja slaydlari uchun juda tez yechim."),
("Photopea: brauzerdagi bepul «Photoshop»", "https://www.photopea.com",
 "O'rnatmasdan ishlaydigan professional rasm muharriri. PSD fayllarni ochadi, qatlamlar, maska, filtrlar bor. Kuchsiz kompyuterda ham ishlaydi.",
 ["Saytni oching, ro'yxatdan o'tish shart emas.", "File → Open orqali rasm yoki PSD shablonni oching.", "Tayyor ishni File → Export as → PNG/JPG qilib saqlang."],
 "Instagram post, banner va vizitka shablonlarini tahrirlash uchun qulay."),
("remove.bg: rasm fonini 5 soniyada olib tashlash", "https://www.remove.bg",
 "Rasmni yuklaysiz, AI fonni avtomatik olib tashlaydi. Mahsulot rasmlari, profil rasmi va reklama dizayni uchun juda qulay.",
 ["Saytga rasm yuklang yoki rasm havolasini qo'ying.", "Natijani ko'ring, kerak bo'lsa «Edit» orqali yangi fon qo'ying.", "Yuklab oling (bepul versiyada o'lcham kichikroq bo'ladi)."],
 "Marketpleys uchun oq fonli mahsulot rasmlari tayyorlashda vaqtni juda tejaydi."),
]

AP = [  # rasmiy AI ilovalar (havola)
("ChatGPT", "com.openai.chatgpt", "https://chatgpt.com",
 "OpenAI'ning rasmiy ilovasi. Ovozli suhbat, rasmni tahlil qilish, fayl bilan ishlash va rasm yaratish bor. Bepul versiyasi ham kuchli."),
("Gemini", "com.google.android.apps.bard", "https://gemini.google.com",
 "Google'ning rasmiy AI yordamchisi. Gmail, Drive, YouTube bilan bog'lanadi, kamera orqali atrofni tushuntiradi."),
("Claude", "com.anthropic.claude", "https://claude.ai",
 "Anthropic'ning rasmiy ilovasi. Uzun matn yozish, tahrirlash, hujjat va kod bilan ishlashda kuchli."),
("Perplexity", "ai.perplexity.app.android", "https://www.perplexity.ai",
 "Internetdan qidirib, manbalari bilan javob beradigan AI. Yangiliklar, narxlar va faktlarni tekshirish uchun qulay."),
]

items = []
for i, (t, what, p) in enumerate(P, 1):
    body = (f"💬 <b>Prompt: {t}</b>\n\n<b>Nima qiladi:</b> {what}\n\n📋 <b>Prompt (bosing, nusxa olinadi):</b>\n{pre(p)}" + FOOT_P)
    assert len(body) < 4000, (t, len(body))
    items.append(dict(cat="prompt", title=t, body=body))
for t, url, what, steps, tip in L:
    body = (f"🌐 <b>Foydali sayt: {t}</b>\n\n{what}\n\n🔗 {url}\n\n<b>Qanday ishlatiladi:</b>\n" +
            "\n".join(f"{k}. {s}" for k, s in enumerate(steps, 1)) + f"\n\n💡 {tip}\n#sayt #ai")
    items.append(dict(cat="link", title=t, body=body, check_urls=[url]))
for name, pkg, site, what in AP:
    play = f"https://play.google.com/store/apps/details?id={pkg}"
    body = (f"📲 <b>Rasmiy ilova: {name}</b>\n\n{what}\n\n"
            f"🤖 Android (Google Play, rasmiy): {play}\n🍏 iPhone: App Store'da «{name}» deb qidiring\n🌐 Sayt: {site}\n\n"
            "⚠️ AI ilovalarini faqat rasmiy do'kondan o'rnating. Noma'lum saytlardagi «Pro/Mod» APK'lar ko'pincha virus yoki akkaunt o'g'irlaydigan dastur bo'ladi.\n#ilova #ai")
    items.append(dict(cat="apklink", title=name, body=body, check_urls=[play, site]))
json.dump(items, open("/home/claude/bot/paid/items_text.json", "w"), ensure_ascii=False, indent=1)
print(len(items))
