// content-pro: yangi yo'nalishlar — darslar (dasturlash, sayt, ilova, video, biznes, AI, freelance),
// GitHub'dagi ochiq loyihalar (zip fayl bilan) va vositalar. Hammasi tekshiriladigan manbaga tayanadi.
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const UA = "Mozilla/5.0 (compatible; ContentBot/1.0)";
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

const TRACKS: Record<string, { tag: string; name: string }> = {
  dasturlash: { tag: "#dasturlash", name: "Dasturlash (Python)" },
  sayt: { tag: "#sayt_yaratish", name: "Sayt yaratish" },
  bot: { tag: "#telegram_bot", name: "Telegram bot yaratish" },
  ilova: { tag: "#ilova_yaratish", name: "Ilova yaratish" },
  video: { tag: "#video_yaratish", name: "Video yaratish" },
  biznes: { tag: "#biznes_boshlash", name: "Biznes boshlash" },
  ai: { tag: "#ai_asoslari", name: "Sun'iy intellekt asoslari" },
  freelance: { tag: "#freelance", name: "Freelance va daromad yo'li" },
};

// src bor bo'lsa — dars shu rasmiy sahifaga tayanadi (ishlamasa dars o'tkazib yuboriladi). src yo'q bo'lsa — faqat umumiy, tushunchaviy dars.
const LESSONS: { t: string; title: string; src?: string }[] = [
  { t: "dasturlash", title: "Python bilan tanishuv: raqamlar, matnlar", src: "https://docs.python.org/3/tutorial/introduction.html" },
  { t: "dasturlash", title: "Shart, tsikl va funksiyalar", src: "https://docs.python.org/3/tutorial/controlflow.html" },
  { t: "dasturlash", title: "Ro'yxat va lug'atlar", src: "https://docs.python.org/3/tutorial/datastructures.html" },
  { t: "dasturlash", title: "Fayllar bilan ishlash", src: "https://docs.python.org/3/tutorial/inputoutput.html" },
  { t: "dasturlash", title: "Xatolarni ushlash (try/except)", src: "https://docs.python.org/3/tutorial/errors.html" },
  { t: "dasturlash", title: "Modullar va tayyor kutubxonalar", src: "https://docs.python.org/3/tutorial/modules.html" },
  { t: "dasturlash", title: "Sinflar (OOP) asoslari", src: "https://docs.python.org/3/tutorial/classes.html" },
  { t: "sayt", title: "Birinchi veb-sahifa: HTML asoslari", src: "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/Basic_HTML_syntax" },
  { t: "sayt", title: "CSS bilan dizayn berish", src: "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Getting_started" },
  { t: "sayt", title: "JavaScript nima va u saytga nima beradi", src: "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/What_is_JavaScript" },
  { t: "sayt", title: "Google Sites bilan kodsiz sayt", src: "https://support.google.com/sites/answer/6372880" },
  { t: "bot", title: "Telegram bot nima va u qanday ishlaydi", src: "https://core.telegram.org/bots/tutorial" },
  { t: "bot", title: "Telegram botlarning imkoniyatlari", src: "https://core.telegram.org/bots/features" },
  { t: "bot", title: "Telegram Mini Apps (bot ichidagi ilova)", src: "https://core.telegram.org/bots/webapps" },
  { t: "ilova", title: "MIT App Inventor bilan kodsiz Android ilova", src: "https://appinventor.mit.edu/explore/ai2/tutorials" },
  { t: "ilova", title: "Flutter bilan birinchi ilova", src: "https://docs.flutter.dev/get-started/codelab" },
  { t: "ilova", title: "Ilova g'oyasini tekshirish va soddalashtirish" },
  { t: "video", title: "Video g'oyasi va ssenariy" },
  { t: "video", title: "Telefonda sifatli kadr olish" },
  { t: "video", title: "Montaj tartibi: xom materialdan tayyor videogacha" },
  { t: "video", title: "Qisqa video (Reels, Shorts) tuzilishi" },
  { t: "video", title: "Subtitr va ovoz: nega kerak" },
  { t: "biznes", title: "Biznes g'oyasini pul sarflamay tekshirish" },
  { t: "biznes", title: "Mijoz portretini aniqlash" },
  { t: "biznes", title: "Oddiy bir sahifali biznes-reja" },
  { t: "biznes", title: "Narx belgilash asoslari" },
  { t: "biznes", title: "Birinchi 10 ta mijozni topish" },
  { t: "biznes", title: "Hisob-kitobni Google Sheets'da yuritish" },
  { t: "biznes", title: "Mijoz bilan muloqot qoidalari" },
  { t: "ai", title: "Yaxshi prompt yozish formulasi" },
  { t: "ai", title: "AI bilan matn va tarjima: xatolarni qanday tekshirish" },
  { t: "ai", title: "AI bilan kod yozish: natijani tekshirish usullari" },
  { t: "ai", title: "AI bilan rasm va dizayn g'oyalari" },
  { t: "freelance", title: "Portfolio yig'ish: birinchi 3 ta ish" },
  { t: "freelance", title: "Birinchi buyurtmani topish yo'llari" },
  { t: "freelance", title: "Ish narxini belgilash va kelishuv" },
];

async function gemini(prompt: string, key: string, temp = 0.4): Promise<A | null> {
  for (const model of ["gemini-3.5-flash-lite", "gemini-3.6-flash"]) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": key },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: temp, responseMimeType: "application/json", maxOutputTokens: 3500 },
        }),
        signal: AbortSignal.timeout(50000),
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

const esc = (s: string) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

async function getText(url: string, ms = 15000, headers: A = {}): Promise<{ status: number; text: string }> {
  const r = await fetch(url, { redirect: "follow", signal: AbortSignal.timeout(ms), headers: { "user-agent": UA, "accept-language": "en", ...headers } });
  const reader = r.body?.getReader();
  let text = "", total = 0;
  const dec = new TextDecoder();
  if (reader) {
    while (total < 600_000) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.length;
      text += dec.decode(value, { stream: true });
    }
    await reader.cancel().catch(() => {});
  }
  return { status: r.status, text };
}

function stripHtml(h: string): string {
  return h.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<nav[\s\S]*?<\/nav>/gi, " ").replace(/<footer[\s\S]*?<\/footer>/gi, " ")
    .replace(/<\/(p|div|li|h\d|pre|tr)>/gi, "\n").replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/[ \t]+/g, " ").replace(/\n\s*\n+/g, "\n").trim();
}

// ---------------------------------------------------------------- DARS
async function buildLesson(l: { t: string; title: string; src?: string }, idx: number, total: number, key: string) {
  let material = "";
  if (l.src) {
    try {
      const r = await getText(l.src);
      if (r.status !== 200) return null;
      material = stripHtml(r.text).slice(0, 7000);
      if (material.length < 800) return null;
    } catch { return null; }
  }
  const tr = TRACKS[l.t];
  const grounded = l.src
    ? `MANBA MATNI (faqat shunga tayan, undan tashqari fakt, tugma nomi yoki kod to'qima; kod misollari faqat manbadan nusxa bo'lsin):\n"""${material}"""`
    : "Manba yo'q: dars faqat umumiy, tushunchaviy bo'lsin. Aniq dastur menyulari, tugma nomlari, narxlar, qonun/soliq qoidalari, statistika yoki daromad raqamlarini YOZMA.";
  const out = await gemini(
    `Sen O'zbekistondagi boshlovchilar uchun amaliy dars yozadigan o'qituvchisan. Mavzu: "${l.title}" (yo'nalish: ${tr.name}). ${grounded}\n` +
      `Oddiy o'zbek tilida (lotin), qisqa gaplar bilan, tushunmovchilik bo'lmasin. Misol va mashq mavzuga xos va aniq bo'lsin (masalan kichik do'kon yoki kafe misolida), umumiy gaplar va takrorlardan qoch. 'prompt' maydoni o'zi yetarli bo'lsin: mavzuni ichiga yozib qo'y, [ ] faqat foydalanuvchi o'z ma'lumotini yozadigan joyda bo'lsin. Daromad va'da qilma. JSON qaytar: ` +
      `{"nima":"1-2 gap: bu darsda nimani o'rganadi","qadamlar":["3-5 ta aniq qisqa qadam"],"misol":"1 ta qisqa amaliy misol (kod bo'lsa manbadan)","mashq":"bugun qiladigan 1 ta kichik topshiriq","prompt":"AI (ChatGPT/Gemini) ga berish uchun tayyor, [ ] bilan to'ldiriladigan qisqa prompt, shu mavzuda o'rganish/mashq uchun"}`,
    key,
  );
  if (!out?.nima || !Array.isArray(out.qadamlar) || out.qadamlar.length < 2 || !out.mashq || !out.prompt) return null;
  const steps = out.qadamlar.slice(0, 5).map((s: string, i: number) => `${i + 1}. ${esc(s)}`).join("\n");
  const body =
    `🎓 <b>DARS · ${esc(tr.name)} · ${idx}/${total}</b>\n<b>${esc(l.title)}</b>\n\n` +
    `📌 <b>Nima o'rganasiz:</b> ${esc(out.nima)}\n\n` +
    `🧭 <b>Qadamlar:</b>\n${steps}\n\n` +
    (out.misol ? `🔎 <b>Misol:</b>\n<pre>${esc(String(out.misol).slice(0, 700))}</pre>\n\n` : "") +
    `✍️ <b>Bugungi mashq:</b> ${esc(out.mashq)}\n\n` +
    `🤖 <b>AI bilan mashq (prompt):</b>\n<pre>${esc(String(out.prompt).slice(0, 600))}</pre>` +
    (l.src ? `\n\n📚 <b>Rasmiy manba:</b> <a href="${l.src}">${new URL(l.src).host}</a>` : "") +
    `\n\n${tr.tag}`;
  if (body.length > 3900) return null;
  return { body, urls: l.src ? [l.src] : [], title: l.title, track: l.t };
}

// ---------------------------------------------------------------- GITHUB LOYIHALAR
const REPO_QUERIES: { q: string; track: string; label: string }[] = [
  { q: "topic:telegram-bot language:python", track: "bot", label: "Telegram bot (Python)" },
  { q: "topic:telegram-bot language:javascript", track: "bot", label: "Telegram bot (JavaScript)" },
  { q: "topic:landing-page topic:template", track: "sayt", label: "Landing sahifa shabloni" },
  { q: "topic:portfolio-website topic:html", track: "sayt", label: "Portfolio sayt shabloni" },
  { q: "topic:website-template language:html", track: "sayt", label: "Sayt shabloni" },
  { q: "topic:flutter topic:template", track: "ilova", label: "Flutter ilova shabloni" },
  { q: "topic:starter-template topic:react", track: "sayt", label: "React boshlang'ich loyiha" },
  { q: "topic:python topic:beginner-project", track: "dasturlash", label: "Python boshlovchi loyiha" },
  { q: "topic:discord-bot language:python", track: "bot", label: "Bot (Python)" },
  { q: "topic:expense-tracker", track: "dasturlash", label: "Xarajat hisobi loyihasi" },
];
const OK_LIC = new Set(["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "CC0-1.0"]);

async function buildRepo(used: Set<string>, key: string, gh: A) {
  const rq = REPO_QUERIES[Math.floor(Math.random() * REPO_QUERIES.length)];
  const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(rq.q + " stars:>200 archived:false")}&sort=stars&per_page=30`;
  const r = await fetch(url, { headers: { "user-agent": UA, accept: "application/vnd.github+json", ...gh }, signal: AbortSignal.timeout(20000) });
  if (!r.ok) { await r.body?.cancel(); return null; }
  const j = await r.json();
  const twoYears = Date.now() - 2 * 365 * 86400000;
  const cands = (j.items ?? []).filter((x: A) =>
    !used.has(`repo:${x.full_name}`) && x.license && OK_LIC.has(x.license.spdx_id) && x.size > 0 && x.size < 14000 &&
    x.description && Date.parse(x.pushed_at) > twoYears && !x.fork);
  const c = cands[0];
  if (!c) return null;
  const rd = await getText(`https://raw.githubusercontent.com/${c.full_name}/HEAD/README.md`, 15000);
  const readme = rd.status === 200 ? rd.text.slice(0, 3500) : "";
  const out = await gemini(
    `Quyidagi ochiq GitHub loyihasi haqida o'zbek tilida (lotin) qisqa va aniq post uchun ma'lumot tayyorla. Faqat berilgan ma'lumotga tayan, to'qima.\n` +
      `Nomi: ${c.full_name}\nTavsif: ${c.description}\nTil: ${c.language}\nLitsenziya: ${c.license.spdx_id}\nREADME (qisqartirilgan):\n"""${readme}"""\n` +
      `JSON: {"nima":"loyiha nima qiladi, 1-2 gap","kimga":"kimlar uchun foydali (boshlovchi, sayt egasi, bot yaratuvchi...)","boshlash":["README'da yozilgan ishga tushirish bo'yicha 2-4 qisqa qadam; README'da bo'lmasa bo'sh massiv; git clone buyrug'ini faqat bir marta va sudo siz yoz"]}`,
    key,
  );
  if (!out?.nima) return null;
  const steps = (out.boshlash ?? []).slice(0, 4).map((s: string, i: number) => `${i + 1}. ${esc(s)}`).join("\n");
  const body =
    `💻 <b>KOD: ${esc(c.full_name.split("/")[1])}</b> · ${esc(rq.label)}\n\n` +
    `📌 <b>Nima qiladi:</b> ${esc(out.nima)}\n` +
    `👥 <b>Kimga kerak:</b> ${esc(out.kimga ?? "")}\n` +
    `🛠 <b>Til:</b> ${esc(c.language ?? "-")} · ⭐ ${c.stargazers_count} · 📄 Litsenziya: ${esc(c.license.spdx_id)} (ochiq, ishlatish mumkin)\n` +
    (steps ? `\n⚙️ <b>Ishga tushirish (README bo'yicha):</b>\n${steps}\n` : "") +
    `\n📦 Loyiha fayllari (zip) pastda, bu xabarga javob sifatida yuboriladi.\n` +
    `🔗 <a href="${c.html_url}">GitHub sahifasi</a>\n⚠️ Ishlatishdan oldin litsenziya va README'ni o'qing.\n\n#kod #github ${TRACKS[rq.track].tag}`;
  if (body.length > 3900) return null;
  return { body, urls: [c.html_url], title: c.full_name, key: `repo:${c.full_name}`, track: rq.track };
}

// ---------------------------------------------------------------- VOSITALAR
const TOOL_THEMES: { track: string; theme: string }[] = [
  { track: "dasturlash", theme: "bepul kod muharrirlari va dasturlashni o'rganish platformalari" },
  { track: "sayt", theme: "bepul/arzon sayt yaratish va hosting platformalari" },
  { track: "ilova", theme: "kodsiz (no-code) ilova yaratish platformalari" },
  { track: "video", theme: "telefon va kompyuterda video montaj dasturlari" },
  { track: "ai", theme: "sun'iy intellekt vositalari (matn, rasm, ovoz)" },
  { track: "biznes", theme: "kichik biznes uchun mijozlar bazasi, to'lov va hisob-kitob vositalari" },
  { track: "freelance", theme: "freelancerlar uchun ish topish va portfolio platformalari" },
];

async function buildTool(used: Set<string>, key: string) {
  const th = TOOL_THEMES[Math.floor(Math.random() * TOOL_THEMES.length)];
  const list = await gemini(
    `Mavzu: ${th.theme}. Dunyoda mashhur, haqiqatan mavjud 8 ta vositani ber. Faqat rasmiy bosh sahifa URL (https://...). Mavjudligiga ishonchsiz bo'lsa qo'shma. JSON: {"items":[{"nom":"...","url":"https://..."}]}`,
    key, 0.6,
  );
  for (const it of list?.items ?? []) {
    try {
      const u = new URL(it.url);
      const host = u.hostname.replace(/^www\./, "");
      const k = `tool:${host}`;
      if (used.has(k) || used.has(`site:${host}`)) continue;
      const r = await getText(u.origin, 15000);
      if (r.status >= 400) continue;
      const title = (r.text.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? "").replace(/\s+/g, " ").trim().slice(0, 120);
      const desc = (r.text.match(/<meta[^>]+(?:name|property)=["'](?:og:)?description["'][^>]+content=["']([^"']+)["']/i)?.[1] ?? "").slice(0, 300);
      if (!title || desc.length < 30) continue;
      const out = await gemini(
        `Sayt: ${u.origin}\nSarlavha: ${title}\nTavsif: ${desc}\nShu ma'lumotga TAYANIB o'zbek tilida (lotin) JSON: {"nima":"vosita nima uchun, 1-2 gap, to'qima","kimga":"kimlar uchun","maslahat":"boshlovchi uchun 1 ta qisqa maslahat (narx va aniq tugma nomlarini aytma)"}`,
        key,
      );
      if (!out?.nima) continue;
      const body =
        `🧰 <b>VOSITA: ${esc(it.nom || host)}</b> · ${esc(TRACKS[th.track].name)}\n\n` +
        `📌 <b>Nima uchun:</b> ${esc(out.nima)}\n👥 <b>Kimga kerak:</b> ${esc(out.kimga ?? "")}\n💡 <b>Maslahat:</b> ${esc(out.maslahat ?? "")}\n` +
        `💰 <b>Narx:</b> rasmiy saytda ko'ring (tariflar o'zgarib turadi).\n\n🔗 <a href="${u.origin}">${host}</a>\n\n#vosita ${TRACKS[th.track].tag}`;
      return { body, urls: [u.origin], title: it.nom || host, key: k, track: th.track };
    } catch { /* keyingisi */ }
  }
  return null;
}

// ---------------------------------------------------------------- ASOSIY
Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value").in("key", ["POSTER_CRON_KEY", "GEMINI_API_KEY", "AUTO_APPROVE", "GITHUB_TOKEN"]);
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? "";
    if (!get("POSTER_CRON_KEY") || req.headers.get("x-cron-key") !== get("POSTER_CRON_KEY")) return new Response("forbidden", { status: 403 });
    const url = new URL(req.url);

    if (url.searchParams.get("probe")) {
      const out: A[] = [];
      await Promise.all(LESSONS.filter((l) => l.src).map(async (l) => {
        try { const r = await getText(l.src!, 12000); out.push({ src: l.src, status: r.status, len: stripHtml(r.text).length }); } catch (e) { out.push({ src: l.src, err: String(e).slice(0, 60) }); }
      }));
      return new Response(JSON.stringify(out.sort((a, b) => String(a.src).localeCompare(String(b.src)))), { headers: { "content-type": "application/json" } });
    }

    const key = get("GEMINI_API_KEY");
    if (!key) return new Response("no GEMINI_API_KEY");
    const status = get("AUTO_APPROVE") === "true" ? "queued" : "draft";
    const gh = get("GITHUB_TOKEN") ? { authorization: `Bearer ${get("GITHUB_TOKEN")}` } : {};

    const { count: backlog } = await sb.from("content_posts").select("id", { count: "exact", head: true }).in("status", ["queued", "draft"]).in("kind", ["guide", "repo", "tool"]);
    if ((backlog ?? 0) >= 24) return new Response(`enough (${backlog})`);

    const { data: usedRows } = await sb.from("content_posts").select("source_key").not("source_key", "is", null);
    const used = new Set<string>((usedRows ?? []).map((r: A) => r.source_key));
    const { data: mx } = await sb.from("content_posts").select("sort_order").order("sort_order", { ascending: false }).limit(1);
    let order = (mx?.[0]?.sort_order ?? 0) + 1;
    const newIds: number[] = [];
    const made: string[] = [];

    async function add(kind: string, k: string, p: A) {
      const { data: ins, error } = await sb.from("content_posts").insert({
        sort_order: order++, kind, title: p.title, body: p.body, status, source_key: k, check_urls: p.urls, origin: "auto", track: p.track,
      }).select("id").single();
      if (error) { console.error("insert", error.message); return; }
      used.add(k); made.push(k); newIds.push(ins.id);
    }

    // 1) darslar: har yo'nalishdan navbatdagi hali chiqmagan dars, aylanma tartibda
    const byTrack: Record<string, A[]> = {};
    LESSONS.forEach((l) => { (byTrack[l.t] ??= []).push(l); });
    const trackNames = Object.keys(byTrack);
    const start = Math.floor(Date.now() / 3600000) % trackNames.length;
    let lessons = 0;
    for (let i = 0; i < trackNames.length && lessons < 3; i++) {
      const tn = trackNames[(start + i) % trackNames.length];
      const arr = byTrack[tn];
      for (let n = 0; n < arr.length; n++) {
        const k = `lesson:${tn}:${n + 1}`;
        if (used.has(k)) continue;
        const p = await buildLesson(arr[n], n + 1, arr.length, key);
        if (p) { await add("guide", k, p); lessons++; } else { console.error("lesson skipped", k); }
        break;
      }
    }
    // 2) GitHub loyiha
    for (let a = 0; a < 3; a++) {
      const p = await buildRepo(used, key, gh).catch((e) => { console.error("repo", String(e)); return null; });
      if (p) { await add("repo", p.key, p); break; }
    }
    // 3) vositalar
    for (let a = 0; a < 2; a++) {
      const p = await buildTool(used, key).catch((e) => { console.error("tool", String(e)); return null; });
      if (p) await add("tool", p.key, p);
    }

    // yangilarni navbat bo'ylab tarqatish (har 1 ta eski postdan keyin bittadan)
    if (newIds.length && status === "queued") {
      const { data: q } = await sb.from("content_posts").select("id,sort_order").eq("status", "queued").order("sort_order");
      const rows = q ?? [];
      const base = rows.length ? rows[0].sort_order : 1;
      const fresh = rows.filter((r: A) => newIds.includes(r.id));
      const rest = rows.filter((r: A) => !newIds.includes(r.id));
      const seq: number[] = [];
      let fi = 0;
      rest.forEach((r: A, i: number) => {
        seq.push(r.id);
        if (fi < fresh.length) seq.push(fresh[fi++].id);
      });
      while (fi < fresh.length) seq.push(fresh[fi++].id);
      for (let i = 0; i < seq.length; i++) await sb.from("content_posts").update({ sort_order: base + i }).eq("id", seq[i]);
    }
    return new Response(JSON.stringify({ made }), { headers: { "content-type": "application/json" } });
  } catch (e) {
    console.error("content-pro", String(e));
    return new Response("error", { status: 500 });
  }
});
