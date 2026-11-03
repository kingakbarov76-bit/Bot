// Kontent generatori. Haqiqiy manbalardan (GitHub n8n shablonlari, YouTube, rasmiy saytlar va ilovalar)
// o'zbekcha postlar tayyorlaydi. Gemini FAQAT matn yozadi, havolalarni o'zi to'qimaydi.
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;

const sb = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  { auth: { persistSession: false } },
);

const GH_REPO = "enescingoz/awesome-n8n-templates";
const PER_RUN = 10;
const BACKLOG_TARGET = 40;
const UA = "Mozilla/5.0 (compatible; ContentBot/1.0)";

// Eng ko'p kerak bo'ladigan yo'nalishlardan boshlanadi
const CAT_PRIORITY = [
  "Telegram", "Google_Drive_and_Google_Sheets", "Gmail_and_Email_Automation", "WhatsApp",
  "OpenAI_and_LLMs", "Forms_and_Surveys", "Instagram_Twitter_Social_Media", "Airtable", "Notion",
  "Slack", "WordPress", "HR_and_Recruitment", "PDF_and_Document_Processing", "Database_and_Storage",
  "Discord", "AI_Research_RAG_and_Data_Analysis", "devops", "Other", "Other_Integrations_and_Use_Cases",
];

const SEED_VIDEOS = [
  "GIZzRGYpCbM", "4cQWJViybAQ", "E2yQelHPUdU", "IDSwx_Kv6AQ", "Hak8yXgFo8Q", "1jDEZGjvXbk", "0R6oMEH8u7s", "0WhxkC7C-ds",
];
const VIDEO_FEEDS = ["UCd_JvWY6R-TLpen3drQ5CvQ"];

// ------------------------------------------------------------------ YORDAMCHILAR
const esc = (s: unknown) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const clip = (s: unknown, n: number) => {
  const t = String(s ?? "").trim();
  return t.length > n ? t.slice(0, n - 1).trimEnd() + "…" : t;
};
const encPath = (p: string) =>
  p.split("/").map((s) => encodeURIComponent(s).replace(/[()'!*]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase())).join("/");

async function urlOk(url: string): Promise<boolean> {
  try {
    const yt = url.match(/^https:\/\/www\.youtube\.com\/watch\?v=[\w-]+/);
    const target = yt ? `https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json` : url;
    const r = await fetch(target, { redirect: "follow", signal: AbortSignal.timeout(10000), headers: { "user-agent": UA } });
    await r.body?.cancel();
    if (yt) return r.status === 200 || r.status === 401;
    return r.status < 500 && r.status !== 404 && r.status !== 410;
  } catch {
    return false;
  }
}

async function getJson(url: string, ms = 20000): Promise<A> {
  const r = await fetch(url, { signal: AbortSignal.timeout(ms), headers: { "user-agent": UA, accept: "application/json" } });
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return await r.json();
}

async function gemini(prompt: string, key: string): Promise<A | null> {
  for (const model of ["gemini-3.5-flash-lite", "gemini-3.6-flash"]) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": key },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.5, responseMimeType: "application/json", maxOutputTokens: 2000 },
        }),
        signal: AbortSignal.timeout(45000),
      });
      if (!r.ok) { await r.body?.cancel(); continue; }
      const j = await r.json();
      const t = (j.candidates?.[0]?.content?.parts ?? []).map((p: A) => p.text ?? "").join("")
        .replace(/^```(?:json)?\s*/i, "").replace(/```\s*$/, "").trim();
      return JSON.parse(t);
    } catch (e) {
      console.error("gemini", model, String(e));
    }
  }
  return null;
}

// ------------------------------------------------------------------ N8N SHABLONLARI
const TYPE_NAMES: Record<string, string> = {
  telegram: "Telegram", telegramTrigger: "Telegram", googleSheets: "Google Sheets", googleSheetsTrigger: "Google Sheets",
  gmail: "Gmail", gmailTrigger: "Gmail", googleDrive: "Google Drive", googleDriveTrigger: "Google Drive",
  googleCalendar: "Google Calendar", googleDocs: "Google Docs", openAi: "OpenAI", lmChatOpenAi: "OpenAI",
  embeddingsOpenAi: "OpenAI", lmChatGoogleGemini: "Google Gemini", lmChatAnthropic: "Anthropic Claude",
  lmChatOllama: "Ollama", whatsApp: "WhatsApp", whatsAppTrigger: "WhatsApp", slack: "Slack", slackTrigger: "Slack",
  discord: "Discord", notion: "Notion", notionTrigger: "Notion", airtable: "Airtable", wordpress: "WordPress",
  supabase: "Supabase", vectorStoreSupabase: "Supabase", postgres: "PostgreSQL", mongoDb: "MongoDB",
  emailReadImap: "Pochta (IMAP)", emailSend: "Pochta (SMTP)", microsoftOutlook: "Outlook", twitter: "X (Twitter)",
  youTube: "YouTube", hubspot: "HubSpot", trello: "Trello", stripe: "Stripe", shopify: "Shopify", pinecone: "Pinecone",
  vectorStorePinecone: "Pinecone", vectorStoreQdrant: "Qdrant", webhook: "Webhook (sayt/forma ulanishi)",
  formTrigger: "n8n forma", scheduleTrigger: "Jadval bo'yicha ishga tushirish", httpRequest: "HTTP so'rov (API)",
  agent: "AI agent", chainLlm: "AI zanjiri", memoryBufferWindow: "AI xotirasi", rssFeedRead: "RSS",
};
const SKIP_TYPES = new Set([
  "stickyNote", "manualTrigger", "set", "if", "switch", "merge", "code", "noOp", "splitInBatches", "function",
  "functionItem", "itemLists", "aggregate", "filter", "wait", "respondToWebhook", "executeWorkflow",
  "executeWorkflowTrigger", "errorTrigger", "sort", "limit", "removeDuplicates", "dateTime", "html", "markdown",
  "extractFromFile", "convertToFile", "splitOut", "summarize", "compareDatasets", "outputParserStructured",
]);
const SITE_OF: Record<string, string> = {
  "Telegram": "telegram.org", "Google Sheets": "sheets.google.com", "Gmail": "gmail.com", "Google Drive": "drive.google.com",
  "Google Calendar": "calendar.google.com", "Google Docs": "docs.google.com", "OpenAI": "platform.openai.com",
  "Google Gemini": "aistudio.google.com", "Anthropic Claude": "console.anthropic.com", "Slack": "slack.com",
  "Discord": "discord.com", "Notion": "notion.so", "Airtable": "airtable.com", "WordPress": "wordpress.org",
  "WhatsApp": "whatsapp.com", "Supabase": "supabase.com", "YouTube": "youtube.com", "Outlook": "outlook.com",
  "Ollama": "ollama.com", "HubSpot": "hubspot.com", "Trello": "trello.com", "Stripe": "stripe.com",
  "Shopify": "shopify.com", "Pinecone": "pinecone.io", "Qdrant": "qdrant.tech", "PostgreSQL": "postgresql.org",
  "MongoDB": "mongodb.com",
};
const CRED_NAMES: [RegExp, string][] = [
  [/^googleSheets/i, "Google Sheets"], [/^gmail/i, "Gmail"], [/^googleDrive/i, "Google Drive"],
  [/^googleCalendar/i, "Google Calendar"], [/^googleDocs/i, "Google Docs"], [/^openAi/i, "OpenAI API kaliti"],
  [/^telegram/i, "Telegram bot tokeni"], [/^slack/i, "Slack"], [/^discord/i, "Discord"], [/^notion/i, "Notion"],
  [/^airtable/i, "Airtable"], [/^wordpress/i, "WordPress"], [/^whatsApp/i, "WhatsApp Business"],
  [/^supabase/i, "Supabase"], [/^postgres/i, "PostgreSQL"], [/^mongoDb/i, "MongoDB"], [/^ollama/i, "Ollama"],
  [/^anthropic/i, "Anthropic API kaliti"], [/^google(Palm|Gemini)/i, "Google Gemini API kaliti"],
  [/^smtp/i, "Pochta (SMTP)"], [/^imap/i, "Pochta (IMAP)"], [/^microsoftOutlook/i, "Outlook"],
  [/^pinecone/i, "Pinecone"], [/^qdrant/i, "Qdrant"], [/^youTube/i, "YouTube"], [/^twitter/i, "X (Twitter)"],
];
const words = (s: string) => s.replace(/([a-z0-9])([A-Z])/g, "$1 $2").replace(/Api$|OAuth2Api$|OAuth2$/i, "").trim();

async function templateCandidates(used: Set<string>): Promise<string[]> {
  const tree = await getJson(`https://api.github.com/repos/${GH_REPO}/git/trees/main?recursive=1`, 25000);
  const paths: string[] = (tree.tree ?? [])
    .filter((n: A) => n.type === "blob" && n.path.endsWith(".json") && n.path.includes("/") && !n.path.startsWith("."))
    .map((n: A) => n.path as string)
    .filter((p: string) => !used.has("tpl:" + p));
  const rank = (p: string) => {
    const i = CAT_PRIORITY.indexOf(p.split("/")[0]);
    return i === -1 ? 999 : i;
  };
  return paths.map((p, i) => ({ p, i })).sort((a, b) => rank(a.p) - rank(b.p) || a.i - b.i).map((x) => x.p);
}

async function buildTemplate(path: string, key: string): Promise<{ title: string; body: string; urls: string[] } | null> {
  const rawUrl = `https://raw.githubusercontent.com/${GH_REPO}/main/${encPath(path)}`;
  const blobUrl = `https://github.com/${GH_REPO}/blob/main/${encPath(path)}`;
  const r = await fetch(rawUrl, { signal: AbortSignal.timeout(20000), headers: { "user-agent": UA } });
  if (!r.ok) { await r.body?.cancel(); return null; }
  const text = await r.text();
  if (text.length > 1_500_000) return null;
  let wf: A;
  try { wf = JSON.parse(text); } catch { return null; }
  const nodes: A[] = Array.isArray(wf.nodes) ? wf.nodes : [];
  if (!nodes.length) return null;

  const name = path.split("/").pop()!.replace(/\.json$/i, "");
  const apps: string[] = [];
  const creds: string[] = [];
  const notes: string[] = [];
  for (const n of nodes) {
    const t = String(n.type ?? "").split(".").pop() ?? "";
    if (t === "stickyNote") {
      const c = String(n.parameters?.content ?? "").replace(/!\[[^\]]*\]\([^)]*\)/g, "").replace(/[#*_`>]/g, " ").replace(/\s+/g, " ").trim();
      if (c) notes.push(c);
      continue;
    }
    if (!SKIP_TYPES.has(t)) {
      const label = TYPE_NAMES[t] ?? words(t.replace(/Trigger$/, ""));
      if (label && !apps.includes(label)) apps.push(label);
    }
    for (const ck of Object.keys(n.credentials ?? {})) {
      const hit = CRED_NAMES.find(([re]) => re.test(ck));
      const label = hit ? hit[1] : words(ck);
      if (label && !creds.includes(label)) creds.push(label);
    }
  }
  const shownApps = apps.slice(0, 7);
  const prompt = `Sen n8n avtomatlashtirish bo'yicha o'zbek tilidagi kontent muharririsan. Quyida n8n shabloni haqida HAQIQIY ma'lumot bor. Faqat shu ma'lumotga tayan, unda yo'q narsani to'qima.

Shablon nomi (inglizcha): ${name}
Ishlatiladigan ilovalar/tugunlar: ${shownApps.join(", ") || "noma'lum"}
Kerakli hisoblar: ${creds.join(", ") || "yo'q"}
Muallifning izohlari (bo'lishi mumkin): ${clip(notes.join(" | "), 1800) || "yo'q"}

Javobni FAQAT JSON qilib ber (lotin yozuvidagi oddiy o'zbek tilida):
{"sarlavha": "qisqa o'zbekcha sarlavha, 70 belgigacha", "nima_qiladi": "1-2 gap: qaysi ishni avtomatlashtiradi", "biznes": "qaysi turdagi bizneslarga mos, 1-2 gap", "qadamlar": ["shablonga xos sozlash qadami", "..."]}
Qoidalar: "qadamlar" 2-4 ta bo'lsin va faqat shablonni sozlashga oid bo'lsin (hisobni ulash, o'z ma'lumotini kiritish, sinash). Narx yoki va'da yozma. Sonlar va xususiyatlarni o'zingdan qo'shma. Texnik atamalarni (workflow, webhook, API) o'zgartirma.`;
  const g = await gemini(prompt, key);
  if (!g || !g.sarlavha || !g.nima_qiladi || !g.biznes) return null;
  const steps: string[] = (Array.isArray(g.qadamlar) ? g.qadamlar : []).map((s: A) => clip(s, 160)).filter(Boolean).slice(0, 4);

  const sites = ["n8n.io", ...shownApps.map((a) => SITE_OF[a]).filter(Boolean)].filter((v, i, a) => a.indexOf(v) === i);
  const lang = name.match(/\((Italian|Spanish|German|French|Portuguese|Russian|Turkish|Arabic|Japanese|Chinese|Korean|Dutch|Polish)\)/i);
  const cost = "n8n'ni o'z serveringizga o'rnatsangiz bepul variant bor." +
    (creds.some((c) => /OpenAI/i.test(c)) ? " OpenAI API pullik (to'lov kartasi kerak)." : "");

  const lines: string[] = [
    `🧩 <b>SHABLON: ${esc(clip(g.sarlavha, 90))}</b>`,
    "",
    `📌 <b>Nima qiladi:</b> ${esc(clip(g.nima_qiladi, 320))}`,
    `📱 <b>Qaysi ilovalar:</b> ${esc(["n8n", ...shownApps].join(" + "))}`,
    `🌐 <b>Qaysi saytlar:</b> ${esc(sites.join(" · "))}`,
    `🏢 <b>Qaysi biznes uchun:</b> ${esc(clip(g.biznes, 260))}`,
  ];
  if (creds.length) lines.push(`🔑 <b>Kerakli hisoblar:</b> ${esc(creds.slice(0, 6).join(", "))}`);
  if (lang) lines.push("", `⚠️ <b>Diqqat:</b> shablon nomida «${esc(lang[1])}» deyilgan, ichidagi matnlar shu tilda bo'lishi mumkin. Import qilgach o'zbekchaga almashtiring.`);
  lines.push(
    "",
    "⚙️ <b>O'rnatish:</b>",
    "1. Pastdagi havolada «Raw» tugmasini bosib, faylni saqlang.",
    "2. n8n'da yangi workflow oching → yuqoridagi ⋯ menyu → <i>Import from file</i>.",
    "3. Hisoblarni <i>Credentials</i> orqali ulang.",
    ...steps.map((s, i) => `${i + 4}. ${esc(s)}`),
    "",
    `💰 <b>Narx:</b> ${esc(cost)}`,
    "📚 <b>Manba:</b> awesome-n8n-templates (mualliflik huquqi asl mualliflarga tegishli).",
    `🔗 <a href="${blobUrl}">Shablon (GitHub)</a>`,
  );
  return { title: clip(g.sarlavha, 120), body: lines.join("\n"), urls: [blobUrl] };
}

// ------------------------------------------------------------------ VIDEOLAR
async function videoCandidates(used: Set<string>): Promise<string[]> {
  const ids: string[] = [];
  for (const id of SEED_VIDEOS) if (!used.has("vid:" + id)) ids.push(id);
  for (const ch of VIDEO_FEEDS) {
    try {
      const r = await fetch(`https://www.youtube.com/feeds/videos.xml?channel_id=${ch}`, { signal: AbortSignal.timeout(15000), headers: { "user-agent": UA } });
      if (!r.ok) { await r.body?.cancel(); continue; }
      const xml = await r.text();
      for (const m of xml.matchAll(/<yt:videoId>([\w-]+)<\/yt:videoId>/g)) {
        if (!used.has("vid:" + m[1]) && !ids.includes(m[1])) ids.push(m[1]);
      }
    } catch (e) { console.error("feed", String(e)); }
  }
  return ids;
}

async function buildVideo(id: string): Promise<{ title: string; body: string; urls: string[] } | null> {
  const url = `https://www.youtube.com/watch?v=${id}`;
  const r = await fetch(`https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json`, { signal: AbortSignal.timeout(10000), headers: { "user-agent": UA } });
  if (r.status !== 200) { await r.body?.cancel(); return null; }
  const o = await r.json();
  const title = String(o.title ?? "");
  if (!/n8n/i.test(title)) return null;
  const body = [
    `🎬 <b>VIDEO: ${esc(clip(title, 100))}</b>`,
    "",
    "📌 <b>Nima haqida:</b> sarlavhasiga ko'ra, n8n bo'yicha o'quv video.",
    "📱 <b>Qaysi ilova:</b> n8n",
    "🌐 <b>Qaysi saytlar:</b> n8n.io · youtube.com",
    "🏢 <b>Kim uchun:</b> avtomatlashtirishni o'rganmoqchi bo'lgan biznes egalari va xodimlar.",
    `📺 <b>Kanal:</b> ${esc(o.author_name ?? "")}`,
    "🗣 <b>Til:</b> video asosan ingliz tilida bo'lishi mumkin. YouTube'da subtitr (CC) va avtomatik tarjimani yoqing.",
    "",
    `🔗 <a href="${url}">Videoni ko'rish</a>`,
  ].join("\n");
  return { title: clip(title, 120), body, urls: [url] };
}

// ------------------------------------------------------------------ PROMPTLAR
const PROMPT_TOPICS: [string, string][] = [
  ["p-first-msg", "Yangi mijozga birinchi xabar (sovuq murojaat)"],
  ["p-offer", "Narx taklifi (tijoriy taklif) matni"],
  ["p-reels", "Instagram Reels uchun ssenariylar"],
  ["p-30days", "Telegram kanal uchun 30 kunlik kontent reja"],
  ["p-sorry", "Norozi mijozga uzr so'rash va muammoni hal qilish xabari"],
  ["p-marketplace", "Marketplace (Uzum, OLX) uchun mahsulot tavsifi"],
  ["p-ads", "Instagram/Facebook reklama matni"],
  ["p-reviews", "Mijoz sharhlarini tahlil qilish"],
  ["p-meeting", "Uchrashuv yozuvidan vazifalar ro'yxati va xulosa"],
  ["p-vacancy", "Vakansiya e'loni yozish"],
  ["p-cv", "Nomzod rezyumesini baholash"],
  ["p-contract", "Shartnoma bandlarini oddiy tilda tushuntirish"],
  ["p-report", "Jadval ma'lumotlaridan hisobot xulosasi"],
  ["p-seo", "Sayt sahifasi uchun sarlavha va tavsif (SEO)"],
  ["p-blog", "Blog maqola rejasi va birinchi qoralama"],
  ["p-newsletter", "Mijozlarga yangiliklar xati (newsletter)"],
  ["p-winback", "Yo'qolgan mijozni qaytarish xabari"],
  ["p-promo", "Chegirma va aksiya e'lonlari"],
  ["p-survey", "Mijozlar so'rovnomasi savollari"],
  ["p-weekly", "Rahbar uchun haftalik reja va ustuvorliklar"],
  ["p-sop", "Xodimlar uchun ish ko'rsatmasi (SOP)"],
  ["p-call", "Telefon orqali sotuv suhbati ssenariysi"],
  ["p-chatbot", "Telegram bot uchun suhbat ssenariysi"],
  ["p-competitor", "Raqobatchilarni tahlil qilish"],
  ["p-swot", "Biznes g'oyani SWOT bilan baholash"],
  ["p-pricing", "Narx belgilash variantlari"],
  ["p-moderation", "Kanal/guruh qoidalari va moderatsiya"],
  ["p-youtube", "YouTube video ssenariysi va sarlavhalari"],
  ["p-supplier", "Yetkazib beruvchiga rasmiy xat"],
  ["p-debt", "To'lovni eslatuvchi xushmuomala xabar"],
  ["p-persona", "Ideal mijoz portretini yaratish"],
  ["p-referral", "Do'st taklif qilish (referal) dasturi matnlari"],
  ["p-naming", "Mahsulot nomi va slogan g'oyalari"],
  ["p-n8n-idea", "Biznes jarayonini n8n avtomatlashtirishga aylantirish rejasi"],
];

async function buildPrompt(id: string, topic: string, key: string): Promise<{ title: string; body: string; urls: string[] } | null> {
  const q = `Sen kichik biznes uchun AI promptlar yozadigan o'zbek tilidagi muharririsan. Mavzu: "${topic}".
Javobni FAQAT JSON qilib ber (lotin yozuvidagi oddiy o'zbek tilida):
{"sarlavha": "qisqa sarlavha, 60 belgigacha", "nima_qiladi": "1-2 gap: bu prompt nimaga yordam beradi", "biznes": "qaysi bizneslar uchun foydali, 1-2 gap", "prompt": "ChatGPT/Claude/Gemini'ga yuboriladigan tayyor prompt matni", "maslahat": "1 gap: natijani qanday tekshirish yoki yaxshilash"}
Prompt qoidalari: o'zbek tilida bo'lsin, foydalanuvchi to'ldiradigan joylar [kvadrat qavsda] bo'lsin, rol berilsin ("Sen ... mutaxassissan"), chiqish formati aniq yozilsin, 600-900 belgi, yolg'on yoki tekshirib bo'lmaydigan va'dalar bo'lmasin.`;
  const g = await gemini(q, key);
  if (!g || !g.sarlavha || !g.nima_qiladi || !g.biznes || !g.prompt) return null;
  const prompt = clip(g.prompt, 1300);
  const lines = [
    `💬 <b>PROMPT: ${esc(clip(g.sarlavha, 90))}</b>`,
    "",
    `📌 <b>Nima qiladi:</b> ${esc(clip(g.nima_qiladi, 300))}`,
    "📱 <b>Qaysi ilova:</b> ChatGPT, Claude yoki Gemini",
    "🌐 <b>Qaysi saytlar:</b> chatgpt.com · claude.ai · gemini.google.com",
    `🏢 <b>Qaysi biznes uchun:</b> ${esc(clip(g.biznes, 260))}`,
    "",
    "⚙️ <b>Qanday ishlatiladi:</b> matnni nusxalang, [ ] ichini o'zingiznikiga almashtiring va AI'ga yuboring.",
    "",
    `<pre>${esc(prompt)}</pre>`,
  ];
  if (g.maslahat) lines.push("", `💡 ${esc(clip(g.maslahat, 220))}`);
  return { title: clip(g.sarlavha, 120), body: lines.join("\n"), urls: [] };
}

// ------------------------------------------------------------------ SAYTLAR VA ILOVALAR
const SITES: { id: string; name: string; url: string; what: string; biz: string }[] = [
  { id: "n8n", name: "n8n", url: "https://n8n.io", what: "Turli ilovalarni bir-biriga ulab, ish jarayonlarini (xabar, jadval, pochta, AI) avtomatlashtiradigan vosita. Tayyor shablonlar bilan tez boshlanadi.", biz: "Sotuv, mijozlar bilan ishlash va hisobotlarni avtomatlashtirmoqchi bo'lgan har qanday kichik va o'rta biznes." },
  { id: "make", name: "Make", url: "https://www.make.com", what: "Ilovalarni vizual sxema orqali bog'laydigan avtomatlashtirish platformasi (n8n'ga muqobil).", biz: "Kod yozmasdan avtomatlashtirishni xohlaydigan bizneslar." },
  { id: "zapier", name: "Zapier", url: "https://zapier.com", what: "Ilovalarni bog'lab, takroriy ishlarni o'zi bajaradigan mashhur xizmat; kod yozish shart emas.", biz: "Kichik jamoalar va yakka tadbirkorlar." },
  { id: "gsheets", name: "Google Sheets", url: "https://sheets.google.com", what: "Bepul onlayn jadval: mijozlar bazasi, hisob-kitob va hisobotlar uchun. n8n va boshqa vositalar bilan oson ulanadi.", biz: "Mijoz va sotuvlarni jadvalda yuritadigan har qanday biznes." },
  { id: "gforms", name: "Google Forms", url: "https://forms.google.com", what: "So'rovnoma va ariza formalarini yaratish; javoblar jadvalga avtomatik tushadi.", biz: "O'quv markazlar, xizmat ko'rsatish, tadbirlar uchun ro'yxatga olish." },
  { id: "botfather", name: "BotFather (Telegram)", url: "https://t.me/BotFather", what: "Telegram'da o'z botingizni yaratish va token olish uchun rasmiy bot.", biz: "Mijozlar bilan Telegram orqali ishlaydigan har qanday biznes." },
  { id: "chatgpt", name: "ChatGPT", url: "https://chatgpt.com", what: "AI yordamchi: matn, reja, tarjima va g'oyalar uchun. Kanaldagi promptlar bilan ishlaydi.", biz: "Matn va kontent bilan ko'p ishlaydigan bizneslar." },
  { id: "claude", name: "Claude", url: "https://claude.ai", what: "AI yordamchi: matn yozish, tahlil va hujjatlar bilan ishlash uchun.", biz: "Hujjat, shartnoma va hisobotlar bilan ishlaydigan bizneslar." },
  { id: "gemini", name: "Google Gemini", url: "https://gemini.google.com", what: "Google'ning AI yordamchisi; Google hisobi bilan ishlaydi.", biz: "Google xizmatlaridan foydalanadigan jamoalar." },
  { id: "aistudio", name: "Google AI Studio", url: "https://aistudio.google.com", what: "Gemini API kalitini olish va AI'ni sinash uchun sayt. Bot yoki avtomatlashtirishga AI ulash uchun kerak bo'ladi.", biz: "O'z botiga yoki avtomatlashtirishiga AI ulamoqchi bo'lganlar." },
  { id: "canva", name: "Canva", url: "https://www.canva.com", what: "Post, reklama va taqdimotlar uchun tayyor dizayn shablonlari.", biz: "Ijtimoiy tarmoqda mahsulot sotadigan bizneslar." },
  { id: "notion", name: "Notion", url: "https://www.notion.so", what: "Vazifalar, bilim bazasi va loyihalarni bir joyda boshqarish uchun ish maydoni.", biz: "Kichik jamoalar va loyiha bilan ishlaydigan kompaniyalar." },
  { id: "trello", name: "Trello", url: "https://trello.com", what: "Vazifalarni kartalar va doskalarda boshqarish; kichik jamoalar uchun qulay.", biz: "Buyurtma va loyiha jarayonini ko'rib turishni xohlaydigan bizneslar." },
  { id: "amocrm", name: "amoCRM", url: "https://www.amocrm.com", what: "Mijozlar va sotuv jarayonini boshqaradigan CRM tizimi.", biz: "Ko'p so'rov va sotuv menejerlari bilan ishlaydigan bizneslar." },
  { id: "bitrix24", name: "Bitrix24", url: "https://www.bitrix24.com", what: "CRM, vazifalar va jamoa muloqotini birlashtirgan tizim.", biz: "Mijoz bazasi va jamoani bir joyda yuritmoqchi bo'lgan bizneslar." },
];
const APPS: { id: string; name: string; pkg: string; what: string; biz: string }[] = [
  { id: "telegram", name: "Telegram", pkg: "org.telegram.messenger", what: "Mijozlar bilan aloqa, kanal va botlar uchun asosiy ilova.", biz: "Mijozlar bilan Telegram orqali ishlaydigan har qanday biznes." },
  { id: "sheets", name: "Google Sheets", pkg: "com.google.android.apps.docs.editors.sheets", what: "Jadvallarni telefondan ko'rish va tahrirlash.", biz: "Mijoz va sotuvlarni jadvalda yuritadigan bizneslar." },
  { id: "wabusiness", name: "WhatsApp Business", pkg: "com.whatsapp.w4b", what: "Biznes uchun WhatsApp: katalog, tezkor javoblar va biznes profili.", biz: "Mijozlar WhatsApp'da yozadigan bizneslar." },
  { id: "gmail", name: "Gmail", pkg: "com.google.android.gm", what: "Ish pochtasini telefondan boshqarish.", biz: "Pochta orqali mijoz va hamkorlar bilan ishlaydigan bizneslar." },
  { id: "gdrive", name: "Google Drive", pkg: "com.google.android.apps.docs", what: "Hujjatlarni bulutda saqlash va jamoa bilan ulashish.", biz: "Hujjat va fayllar bilan ishlaydigan jamoalar." },
  { id: "canva", name: "Canva", pkg: "com.canva.editor", what: "Telefonda post va reklama dizayni.", biz: "Ijtimoiy tarmoqda mahsulot sotadigan bizneslar." },
  { id: "chatgpt", name: "ChatGPT", pkg: "com.openai.chatgpt", what: "AI yordamchi telefonda: matn, g'oya, tarjima.", biz: "Tezkor matn va g'oya kerak bo'ladigan bizneslar." },
  { id: "claude", name: "Claude", pkg: "com.anthropic.claude", what: "AI yordamchi telefonda: matn va tahlil.", biz: "Hujjat va matn bilan ishlaydigan bizneslar." },
  { id: "gemini", name: "Google Gemini", pkg: "com.google.android.apps.bard", what: "Google'ning AI yordamchisi telefonda.", biz: "Google xizmatlaridan foydalanadigan jamoalar." },
  { id: "gcal", name: "Google Calendar", pkg: "com.google.android.calendar", what: "Uchrashuv va vazifalarni rejalashtirish.", biz: "Jadval bo'yicha ishlaydigan xizmat bizneslari." },
];

function buildSite(s: (typeof SITES)[number]) {
  const body = [
    `🌐 <b>SAYT: ${esc(s.name)}</b>`,
    "",
    `📌 <b>Nima uchun kerak:</b> ${esc(s.what)}`,
    `🏢 <b>Qaysi biznes uchun:</b> ${esc(s.biz)}`,
    "💰 <b>Narx:</b> bepul va pullik tariflar bo'lishi mumkin, joriy narxni saytning o'zida tekshiring.",
    "",
    `🔗 <a href="${s.url}">${esc(s.url.replace(/^https?:\/\//, ""))}</a>`,
  ].join("\n");
  return { title: s.name, body, urls: [s.url] };
}
function buildApp(a: (typeof APPS)[number]) {
  const url = `https://play.google.com/store/apps/details?id=${a.pkg}`;
  const body = [
    `📲 <b>ILOVA: ${esc(a.name)}</b>`,
    "",
    `📌 <b>Nima uchun kerak:</b> ${esc(a.what)}`,
    `🏢 <b>Qaysi biznes uchun:</b> ${esc(a.biz)}`,
    "🛡 <b>Xavfsizlik:</b> faqat rasmiy do'kondan (Google Play yoki App Store) yuklang. Boshqa saytlardagi APK fayllar telefoningizga zarar yetkazishi mumkin.",
    "",
    `🔗 <a href="${url}">Google Play (Android)</a>`,
  ].join("\n");
  return { title: a.name, body, urls: [url] };
}

// ------------------------------------------------------------------ ASOSIY
Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value").in("key", ["POSTER_CRON_KEY", "GEMINI_API_KEY", "AUTO_APPROVE"]);
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? "";
    if (!get("POSTER_CRON_KEY") || req.headers.get("x-cron-key") !== get("POSTER_CRON_KEY")) {
      return new Response("forbidden", { status: 403 });
    }
    const key = get("GEMINI_API_KEY");
    if (!key) return new Response("no GEMINI_API_KEY");
    const status = get("AUTO_APPROVE") === "true" ? "queued" : "draft";

    const { count: backlog } = await sb.from("content_posts").select("id", { count: "exact", head: true })
      .or("status.eq.queued,and(status.eq.draft,origin.eq.auto)");
    if ((backlog ?? 0) >= BACKLOG_TARGET) return new Response(`enough (${backlog})`);

    const { data: usedRows } = await sb.from("content_posts").select("source_key").not("source_key", "is", null);
    const used = new Set<string>((usedRows ?? []).map((r: A) => r.source_key));
    const { data: maxRow } = await sb.from("content_posts").select("sort_order").order("sort_order", { ascending: false }).limit(1).maybeSingle();
    let order = (maxRow?.sort_order ?? 0) + 1;

    const tpl = await templateCandidates(used).catch((e) => { console.error("tree", String(e)); return [] as string[]; });
    const vid = await videoCandidates(used);
    const prm = PROMPT_TOPICS.filter(([id]) => !used.has("prm:" + id));
    const sit = SITES.filter((s) => !used.has("site:" + s.id));
    const app = APPS.filter((a) => !used.has("app:" + a.id));

    // Kunlik aralashma: shablon, prompt, shablon, video, shablon, prompt, sayt/ilova, ...
    const pattern = ["template", "prompt", "template", "video", "template", "prompt", "site", "template", "prompt", "app"];
    const made: string[] = [];
    let tries = 0;
    for (let i = 0; made.length < PER_RUN && tries < PER_RUN * 4; i++, tries++) {
      const kind = pattern[i % pattern.length];
      let res: { title: string; body: string; urls: string[] } | null = null;
      let sourceKey = "";
      try {
        if (kind === "template") {
          const p = tpl.shift(); if (!p) continue;
          sourceKey = "tpl:" + p;
          res = await buildTemplate(p, key);
        } else if (kind === "prompt") {
          const t = prm.shift(); if (!t) continue;
          sourceKey = "prm:" + t[0];
          res = await buildPrompt(t[0], t[1], key);
        } else if (kind === "video") {
          const v = vid.shift(); if (!v) continue;
          sourceKey = "vid:" + v;
          res = await buildVideo(v);
        } else if (kind === "site") {
          const s = sit.shift(); if (!s) continue;
          sourceKey = "site:" + s.id;
          res = buildSite(s);
        } else {
          const a = app.shift(); if (!a) continue;
          sourceKey = "app:" + a.id;
          res = buildApp(a);
        }
        if (!res) continue;
        if (res.body.length > 3900) continue;
        const ok = await Promise.all(res.urls.map(urlOk));
        if (ok.some((x) => !x)) { console.error("url not ok", res.urls.join(",")); continue; }
        const { error } = await sb.from("content_posts").insert({
          sort_order: order++, kind, title: res.title, body: res.body, status,
          source_key: sourceKey, check_urls: res.urls, origin: "auto",
        });
        if (error) { console.error("insert", error.message); continue; }
        made.push(`${kind}:${sourceKey}`);
      } catch (e) {
        console.error("build", kind, String(e));
      }
    }
    return new Response(JSON.stringify({ status, made: made.length, items: made }), { headers: { "content-type": "application/json" } });
  } catch (e) {
    console.error("content-gen", String(e));
    return new Response("error", { status: 500 });
  }
});
