// Cheksiz kontent manbalari: n8n rasmiy shablon bazasi (13 000+), prompts.chat (awesome-chatgpt-prompts),
// AI taklif qilgan yangi mavzular, hamda tekshirilgan saytlar va Google Play ilovalari.
// Hech narsa takrorlanmaydi: har bir manba source_key bilan yagona.
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const sb = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  { auth: { persistSession: false } },
);
const UA = "Mozilla/5.0 (compatible; ContentBot/1.0)";
const PER_RUN = 10;
const BACKLOG_MAX = 60;

const esc = (s: unknown) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const clip = (s: unknown, n: number) => {
  const t = String(s ?? "").trim();
  return t.length > n ? t.slice(0, n - 1).trimEnd() + "…" : t;
};
const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);

async function gemini(prompt: string, key: string, temp = 0.5): Promise<A | null> {
  for (const model of ["gemini-3.5-flash-lite", "gemini-3.6-flash"]) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": key },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: temp, responseMimeType: "application/json", maxOutputTokens: 2500 },
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

async function fetchText(url: string, ms = 15000): Promise<{ status: number; text: string }> {
  const r = await fetch(url, { redirect: "follow", signal: AbortSignal.timeout(ms), headers: { "user-agent": UA, "accept-language": "en" } });
  const text = await r.text();
  return { status: r.status, text };
}
function meta(html: string) {
  const title = (html.match(/<title[^>]*>([^<]*)<\/title>/i)?.[1] ?? "").replace(/\s+/g, " ").trim();
  const m1 = html.match(/<meta[^>]+(?:name|property)=["'](?:og:)?description["'][^>]*content=["']([^"']*)["']/i);
  const m2 = html.match(/<meta[^>]+content=["']([^"']*)["'][^>]*(?:name|property)=["'](?:og:)?description["']/i);
  const desc = (m1?.[1] ?? m2?.[1] ?? "").replace(/&amp;/g, "&").replace(/&#39;|&apos;/g, "'").replace(/&quot;/g, '"').replace(/\s+/g, " ").trim();
  return { title, desc };
}

type Post = { title: string; body: string; urls: string[] };

const stepsOf = (g: A) =>
  (Array.isArray(g.qadamlar) ? g.qadamlar : []).map((s: A) => clip(s, 260))
    .filter((s: string) => s && !/import|credential|(kaliti|token).*ulang/i.test(s)).slice(0, 3);

// ------------------------------------------------------------------ N8N RASMIY SHABLONLAR
async function n8nBatch(used: Set<string>, need: number): Promise<A[]> {
  const { data } = await sb.from("bot_config").select("value").eq("key", "N8N_PAGE").maybeSingle();
  let page = Number(data?.value ?? "1") || 1;
  const out: A[] = [];
  for (let hop = 0; hop < 6 && out.length < need; hop++, page++) {
    try {
      const r = await fetch(`https://api.n8n.io/api/templates/search?page=${page}&rows=20&sort_by=views:desc`, { signal: AbortSignal.timeout(20000), headers: { "user-agent": UA } });
      if (!r.ok) { await r.body?.cancel(); break; }
      const j = await r.json();
      const list: A[] = j.workflows ?? [];
      if (!list.length) { page = 0; continue; }
      for (const w of list) {
        if (out.length >= need) break;
        if (Number(w.price ?? 0) > 0 || w.purchaseUrl) continue;
        if (used.has("n8n:" + w.id)) continue;
        if (!w.description || String(w.description).length < 80) continue;
        out.push(w);
      }
    } catch (e) { console.error("n8n api", String(e)); break; }
  }
  await sb.from("bot_config").upsert({ key: "N8N_PAGE", value: String(page) });
  return out;
}

async function buildN8n(w: A, key: string): Promise<Post | null> {
  const apps: string[] = [];
  for (const n of (w.nodes ?? []) as A[]) {
    const cats: string[] = (n.nodeCategories ?? []).map((c: A) => c.name);
    if (cats.includes("Core Nodes") && !/Webhook|Schedule|Form|HTTP|Email|AI Agent/i.test(n.displayName ?? "")) continue;
    const dn = String(n.displayName ?? "").replace(/ Trigger$/i, "");
    if (dn && !apps.includes(dn)) apps.push(dn);
  }
  const shown = apps.slice(0, 7);
  const prompt = `Sen n8n avtomatlashtirish bo'yicha o'zbek tilidagi kontent muharririsan. Quyida n8n shabloni haqida HAQIQIY ma'lumot bor. Faqat shu ma'lumotga tayan, unda yo'q narsani to'qima.

Shablon nomi: ${w.name}
Ishlatiladigan ilovalar: ${shown.join(", ") || "noma'lum"}
Muallif tavsifi (inglizcha): ${clip(w.description, 2200)}

Javobni FAQAT JSON qilib ber (lotin yozuvidagi oddiy o'zbek tilida):
{"sarlavha": "qisqa o'zbekcha sarlavha, 70 belgigacha", "nima_qiladi": "1-2 gap: qaysi ishni avtomatlashtiradi", "biznes": "qaysi turdagi bizneslarga mos, 1-2 gap", "qadamlar": ["shablonga xos sozlash qadami", "..."]}
Qoidalar: "qadamlar" 2-3 ta: faqat shablonga xos sozlash (qaysi jadval/papka/chat ID/matn o'zgartiriladi, qanday sinab ko'riladi), har biri bitta qisqa gap (150 belgigacha). Import qilish va hisob ulashni YOZMA. Narx yoki va'da yozma, sonlarni o'zingdan qo'shma.`;
  const g = await gemini(prompt, key);
  if (!g || !g.sarlavha || !g.nima_qiladi || !g.biznes) return null;
  const steps: string[] = stepsOf(g);
  const url = `https://n8n.io/workflows/${w.id}/`;
  const author = w.user?.name ? String(w.user.name) : "";
  const lines = [
    `🧩 <b>SHABLON: ${esc(clip(g.sarlavha, 90))}</b>`,
    "",
    `📌 <b>Nima qiladi:</b> ${esc(clip(g.nima_qiladi, 320))}`,
    `📱 <b>Qaysi ilovalar:</b> ${esc(["n8n", ...shown].join(" + "))}`,
    "🌐 <b>Qaysi saytlar:</b> n8n.io",
    `🏢 <b>Qaysi biznes uchun:</b> ${esc(clip(g.biznes, 260))}`,
    "",
    "⚙️ <b>O'rnatish:</b>",
    "1. Pastdagi sahifani oching va «Use workflow» tugmasini bosing.",
    "2. JSON'ni nusxalang va n8n'da yangi workflow'ga qo'ying (Ctrl+V), yoki n8n Cloud'ga to'g'ridan-to'g'ri import qiling.",
    "3. Kerakli hisoblarni <i>Credentials</i> orqali ulang.",
    ...steps.map((s, i) => `${i + 4}. ${esc(s)}`),
    "",
    "💰 <b>Narx:</b> shablon bepul. n8n'ni o'z serveringizga o'rnatsangiz bepul variant bor, ba'zi ulangan xizmatlar (masalan OpenAI) pullik bo'lishi mumkin.",
    `📚 <b>Manba:</b> n8n.io rasmiy shablonlar bazasi${author ? ", muallif: " + esc(clip(author, 40)) : ""}.`,
    `🔗 <a href="${url}">Shablon sahifasi (n8n.io)</a>`,
  ];
  return { title: clip(g.sarlavha, 120), body: lines.join("\n"), urls: [url] };
}

// ------------------------------------------------------------------ PROMPTLAR
function parseCsv(t: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [], f = "", q = false;
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (q) {
      if (c === '"') { if (t[i + 1] === '"') { f += '"'; i++; } else q = false; } else f += c;
    } else if (c === '"') q = true;
    else if (c === ",") { row.push(f); f = ""; }
    else if (c === "\n") { row.push(f.replace(/\r$/, "")); rows.push(row); row = []; f = ""; }
    else f += c;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  return rows;
}
const BIZ_ACT = /market|sales|seo|copywrit|advertis|accountant|financ|recruit|hr |customer|business|entrepreneur|startup|social media|email|product manager|project manager|negotiat|brand|content|blog|pitch|invest|consult|presentation|resume|cover letter|interview|translator|proofread|support|e-commerce|ecommerce|real estate|salesperson|strategist|analyst|manager|coach/i;

async function readCapped(url: string, maxBytes: number): Promise<string> {
  const r = await fetch(url, { signal: AbortSignal.timeout(30000), headers: { "user-agent": UA, range: `bytes=0-${maxBytes}` } });
  if (!r.ok || !r.body) return "";
  const reader = r.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  while (total < maxBytes) {
    const { done, value } = await reader.read();
    if (done || !value) break;
    chunks.push(value); total += value.length;
  }
  await reader.cancel().catch(() => {});
  const buf = new Uint8Array(total);
  let o = 0;
  for (const c of chunks) { buf.set(c, o); o += c.length; }
  return new TextDecoder().decode(buf);
}

async function promptCandidates(used: Set<string>): Promise<{ act: string; text: string }[]> {
  try {
    const text = await readCapped("https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv", 1_000_000);
    if (!text) return [];
    const rows = parseCsv(text);
    rows.pop(); // oxirgi qator to'liq bo'lmasligi mumkin
    const out: { act: string; text: string }[] = [];
    for (const r of rows.slice(1)) {
      const [act, p, forDevs, type] = r;
      if (!act || !p || String(forDevs).toUpperCase() === "TRUE" || (type && type !== "TEXT")) continue;
      if (p.length > 1500 || p.length < 80) continue;
      if (!BIZ_ACT.test(act)) continue;
      if (used.has("awp:" + slug(act))) continue;
      out.push({ act, text: p });
    }
    return out;
  } catch (e) { console.error("csv", String(e)); return []; }
}

function promptPost(g: A, source: string): Post | null {
  if (!g || !g.sarlavha || !g.nima_qiladi || !g.biznes || !g.prompt) return null;
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
    `<pre>${esc(clip(g.prompt, 1300))}</pre>`,
  ];
  if (g.maslahat) lines.push("", `💡 ${esc(clip(g.maslahat, 220))}`);
  if (source) lines.push("", source);
  return { title: clip(g.sarlavha, 120), body: lines.join("\n"), urls: [] };
}
const PROMPT_JSON = `{"sarlavha": "qisqa sarlavha, 60 belgigacha", "nima_qiladi": "1-2 gap: bu prompt nimaga yordam beradi", "biznes": "qaysi bizneslar uchun foydali, 1-2 gap", "prompt": "tayyor prompt matni", "maslahat": "1 gap: natijani qanday tekshirish yoki yaxshilash"}`;
const PROMPT_RULES = `Prompt qoidalari: o'zbek tilida (lotin), foydalanuvchi to'ldiradigan joylar [kvadrat qavsda], rol berilsin ("Sen ... mutaxassissan"), chiqish formati aniq, 500-900 belgi, yolg'on va'dalar yo'q.`;

async function buildAwesomePrompt(c: { act: string; text: string }, key: string): Promise<Post | null> {
  const q = `Sen kichik biznes uchun AI promptlar tayyorlaydigan o'zbek muharririsan. Quyida inglizcha prompt bor (rol: "${c.act}"). Uni o'zbek tiliga moslab, O'zbekiston kichik biznesi uchun foydali, to'ldiriladigan joylari [kvadrat qavsda] bo'lgan tayyor promptga aylantir. Ma'nosini buzma.

Asl prompt: ${clip(c.text, 1400)}

Javobni FAQAT JSON qilib ber:
${PROMPT_JSON}
${PROMPT_RULES}`;
  return promptPost(await gemini(q, key), "📚 <b>G'oya manbai:</b> prompts.chat (awesome-chatgpt-prompts, CC0).");
}

async function newTopics(key: string, n: number): Promise<string[]> {
  const { data } = await sb.from("content_posts").select("title").eq("kind", "prompt").order("id", { ascending: false }).limit(80);
  const have = (data ?? []).map((r: A) => r.title).join("; ");
  const g = await gemini(`O'zbekiston kichik biznesi uchun ChatGPT/Claude/Gemini promptlari mavzularini taklif qil. Quyidagilar allaqachon bor, ularni takrorlama: ${have || "yo'q"}.
Javob FAQAT JSON: {"mavzular": ["mavzu 1", "..."]} - ${n} ta yangi, aniq amaliy mavzu (sotuv, mijoz, kontent, HR, moliya, jarayonlar, e-commerce, Telegram/Instagram savdosi va hokazo), o'zbek tilida, har biri 3-10 so'z.`, key, 0.9);
  return (Array.isArray(g?.mavzular) ? g.mavzular : []).map((s: A) => String(s)).filter((s: string) => s.length > 5);
}
async function buildTopicPrompt(topic: string, key: string): Promise<Post | null> {
  const q = `Sen kichik biznes uchun AI promptlar yozadigan o'zbek muharririsan. Mavzu: "${topic}".
Javobni FAQAT JSON qilib ber:
${PROMPT_JSON}
${PROMPT_RULES}`;
  return promptPost(await gemini(q, key), "");
}

// ------------------------------------------------------------------ SAYTLAR VA ILOVALAR (tekshiriladi)
async function candidates(kind: "site" | "app", used: Set<string>, key: string): Promise<A[]> {
  const usedList = [...used].filter((k) => k.startsWith(kind + ":")).map((k) => k.slice(kind.length + 1)).slice(-150).join(", ");
  const q = kind === "site"
    ? `Kichik biznesni avtomatlashtirish va rivojlantirish uchun HAQIQIY, mashhur onlayn xizmatlarni ayt (CRM, hisob-faktura, bron/uchrashuv, chatbot, email marketing, forma, to'lov, dizayn, loyiha boshqaruvi, mijozlarga yordam, AI vositalari, O'zbekistonda ishlatiladigan Payme, Click, Uzum kabilar ham). Quyidagilar allaqachon bor, ularni takrorlama: ${usedList || "yo'q"}.
Javob FAQAT JSON: {"items": [{"name": "nomi", "url": "https://asosiy-sayt-manzili"}]} - 12 ta. Faqat aniq bilgan, mavjud saytlarni yoz.`
    : `Kichik biznes uchun foydali HAQIQIY Android ilovalarni ayt (CRM, hisob-kitob, kassa, vazifalar, jadval, chat, dizayn, AI yordamchi, skaner, to'lov, kalendar va hokazo). Quyidagi Google Play paketlari allaqachon bor, takrorlama: ${usedList || "yo'q"}.
Javob FAQAT JSON: {"items": [{"name": "nomi", "package": "com.example.app"}]} - 12 ta. Faqat Google Play'dagi aniq paket nomini bilganlarni yoz.`;
  const g = await gemini(q, key, 0.8);
  return Array.isArray(g?.items) ? g.items : [];
}

async function buildSite(c: A, key: string): Promise<{ post: Post; k: string } | null> {
  let u: URL;
  try { u = new URL(String(c.url)); } catch { return null; }
  if (u.protocol !== "https:") return null;
  const host = u.hostname.replace(/^www\./, "");
  const url = `${u.protocol}//${u.hostname}${u.pathname === "/" ? "" : u.pathname}`;
  const { status, text } = await fetchText(url).catch(() => ({ status: 0, text: "" }));
  if (status >= 400 || status === 0) return null;
  const m = meta(text);
  if (!m.title || !m.desc) return null;
  const g = await gemini(`Sen o'zbek tilidagi kontent muharririsan. Quyida saytning HAQIQIY ma'lumoti (inglizcha yoki boshqa tilda). Faqat shunga tayan, to'qima.
Sayt: ${c.name} (${url})
Sarlavha: ${m.title}
Tavsif: ${m.desc}
Javob FAQAT JSON (lotin yozuvidagi oddiy o'zbek tilida): {"nima_uchun": "1-2 gap: sayt nima uchun kerak", "biznes": "qaysi bizneslarga mos, 1-2 gap"}`, key);
  if (!g?.nima_uchun || !g?.biznes) return null;
  const body = [
    `🌐 <b>SAYT: ${esc(clip(c.name, 60))}</b>`,
    "",
    `📌 <b>Nima uchun kerak:</b> ${esc(clip(g.nima_uchun, 320))}`,
    `🏢 <b>Qaysi biznes uchun:</b> ${esc(clip(g.biznes, 260))}`,
    "💰 <b>Narx:</b> bepul va pullik tariflar bo'lishi mumkin, joriy narxni saytning o'zida tekshiring.",
    "",
    `🔗 <a href="${url}">${esc(host)}</a>`,
  ].join("\n");
  return { post: { title: clip(c.name, 120), body, urls: [url] }, k: "site:" + host };
}

async function buildApp(c: A, key: string): Promise<{ post: Post; k: string } | null> {
  const pkg = String(c.package ?? "").trim();
  if (!/^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$/i.test(pkg)) return null;
  const url = `https://play.google.com/store/apps/details?id=${pkg}&hl=en`;
  const { status, text } = await fetchText(url).catch(() => ({ status: 0, text: "" }));
  if (status !== 200) return null;
  const m = meta(text);
  const name = m.title.replace(/\s*-\s*Apps on Google Play.*$/i, "").trim();
  if (!name || !m.desc) return null;
  const g = await gemini(`Sen o'zbek tilidagi kontent muharririsan. Quyida Android ilovaning Google Play'dagi HAQIQIY ma'lumoti. Faqat shunga tayan, to'qima.
Ilova: ${name}
Tavsif: ${m.desc}
Javob FAQAT JSON (lotin yozuvidagi oddiy o'zbek tilida): {"nima_uchun": "1-2 gap: ilova nima uchun kerak", "biznes": "qaysi bizneslarga mos, 1-2 gap"}`, key);
  if (!g?.nima_uchun || !g?.biznes) return null;
  const body = [
    `📲 <b>ILOVA: ${esc(clip(name, 60))}</b>`,
    "",
    `📌 <b>Nima uchun kerak:</b> ${esc(clip(g.nima_uchun, 320))}`,
    `🏢 <b>Qaysi biznes uchun:</b> ${esc(clip(g.biznes, 260))}`,
    "🛡 <b>Xavfsizlik:</b> faqat rasmiy do'kondan (Google Play yoki App Store) yuklang. Boshqa saytlardagi APK fayllar telefoningizga zarar yetkazishi mumkin.",
    "",
    `🔗 <a href="https://play.google.com/store/apps/details?id=${pkg}">Google Play (Android)</a>`,
  ].join("\n");
  return { post: { title: clip(name, 120), body, urls: [`https://play.google.com/store/apps/details?id=${pkg}`] }, k: "app:" + pkg };
}

// ------------------------------------------------------------------ ASOSIY
Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value").in("key", ["POSTER_CRON_KEY", "GEMINI_API_KEY", "AUTO_APPROVE"]);
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? "";
    if (!get("POSTER_CRON_KEY") || req.headers.get("x-cron-key") !== get("POSTER_CRON_KEY")) return new Response("forbidden", { status: 403 });
    const key = get("GEMINI_API_KEY");
    if (!key) return new Response("no GEMINI_API_KEY");
    const status = get("AUTO_APPROVE") === "true" ? "queued" : "draft";

    const { count: backlog } = await sb.from("content_posts").select("id", { count: "exact", head: true }).in("status", ["queued", "draft"]);
    if ((backlog ?? 0) >= BACKLOG_MAX) return new Response(`enough (${backlog})`);

    const { data: usedRows } = await sb.from("content_posts").select("source_key").not("source_key", "is", null);
    const used = new Set<string>((usedRows ?? []).map((r: A) => r.source_key));
    const { data: maxRow } = await sb.from("content_posts").select("sort_order").order("sort_order", { ascending: false }).limit(1).maybeSingle();
    let order = (maxRow?.sort_order ?? 0) + 1;

    const pattern = ["n8n", "prompt", "n8n", "site", "n8n", "prompt", "app", "n8n", "prompt", "site"];
    const need = (k: string) => pattern.filter((p) => p === k).length;
    const n8nList = await n8nBatch(used, need("n8n") + 4);
    const awesome = await promptCandidates(used);
    let topics: string[] = [];
    const siteC: A[] = (await candidates("site", used, key)).filter((c) => { try { return !used.has("site:" + new URL(c.url).hostname.replace(/^www\./, "")); } catch { return false; } });
    const appC: A[] = (await candidates("app", used, key)).filter((c) => c?.package && !used.has("app:" + c.package));

    const made: string[] = [];
    let tries = 0, awesomeToggle = 0;
    for (let i = 0; made.length < PER_RUN && tries < PER_RUN * 4; i++, tries++) {
      const kind = pattern[i % pattern.length];
      let post: Post | null = null;
      let sk = "";
      let outKind = "";
      try {
        if (kind === "n8n") {
          const w = n8nList.shift(); if (!w) continue;
          sk = "n8n:" + w.id; outKind = "template";
          post = await buildN8n(w, key);
        } else if (kind === "prompt") {
          outKind = "prompt";
          if (awesomeToggle++ % 2 === 0 && awesome.length) {
            const c = awesome.shift()!; sk = "awp:" + slug(c.act);
            post = await buildAwesomePrompt(c, key);
          } else {
            if (!topics.length) topics = await newTopics(key, 4);
            const t = topics.shift(); if (!t) continue;
            sk = "prm:g:" + slug(t) ;
            if (used.has(sk)) continue;
            post = await buildTopicPrompt(t, key);
          }
        } else if (kind === "site") {
          outKind = "site";
          const c = siteC.shift(); if (!c) continue;
          const r = await buildSite(c, key); if (!r) continue;
          post = r.post; sk = r.k;
          if (used.has(sk)) continue;
        } else {
          outKind = "app";
          const c = appC.shift(); if (!c) continue;
          const r = await buildApp(c, key); if (!r) continue;
          post = r.post; sk = r.k;
          if (used.has(sk)) continue;
        }
        if (!post || !sk) { if (sk) used.add(sk); continue; }
        if (post.body.length > 3900) continue;
        const { error } = await sb.from("content_posts").insert({
          sort_order: order++, kind: outKind, title: post.title, body: post.body, status,
          source_key: sk, check_urls: post.urls, origin: "auto",
        });
        if (error) { console.error("insert", error.message); continue; }
        used.add(sk);
        made.push(sk);
      } catch (e) {
        console.error("build", kind, String(e));
      }
    }
    return new Response(JSON.stringify({ status, made: made.length, items: made }), { headers: { "content-type": "application/json" } });
  } catch (e) {
    console.error("content-more", String(e));
    return new Response("error", { status: 500 });
  }
});
