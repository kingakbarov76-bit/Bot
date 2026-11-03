// Kanalga kontent yuboruvchi funksiya (v2). pg_cron uni kuniga 10 marta chaqiradi.
// Yuborishdan oldin havolalarni tekshiradi; buzuq postni o'tkazib yuboradi; xatoda adminga xabar beradi.
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const CHANNEL_ID = Number(Deno.env.get("CHANNEL_ID") ?? "-1004330179807");
const ADMIN_ID = Number(Deno.env.get("ADMIN_ID") ?? "5306954983");
const UA = "Mozilla/5.0 (compatible; ContentBot/1.0)";
const sb = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  { auth: { persistSession: false } },
);

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

async function alertAdmin(text: string, get: (k: string) => string) {
  try {
    const bot = get("BOT_TOKEN");
    if (!bot) return;
    // Xabarlar ko'payib ketmasligi uchun: oxirgi ogohlantirishdan 6 soat o'tgan bo'lsa yuboramiz
    const last = Number(get("LAST_ALERT") || "0");
    if (Date.now() - last < 6 * 3600 * 1000) return;
    await sb.from("bot_config").upsert({ key: "LAST_ALERT", value: String(Date.now()) });
    await fetch(`https://api.telegram.org/bot${bot}/sendMessage`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ chat_id: ADMIN_ID, text: "⚠️ Kontent boti: " + text }),
    });
  } catch (e) {
    console.error("alert", String(e));
  }
}


// ---------------------------------------------------------------- FAYL + QO'SHIMCHA
const TG = (token: string, m: string) => `https://api.telegram.org/bot${token}/${m}`;
const GH_RAW = "https://raw.githubusercontent.com/enescingoz/awesome-n8n-templates/main/";

// ilova nomi -> [sayt, Google Play paketi (rasmiy)]
const APPS: Record<string, [string, string?]> = {
  "gmail": ["https://mail.google.com", "com.google.android.gm"],
  "google sheets": ["https://sheets.google.com", "com.google.android.apps.docs.editors.sheets"],
  "google docs": ["https://docs.google.com", "com.google.android.apps.docs.editors.docs"],
  "google drive": ["https://drive.google.com", "com.google.android.apps.docs"],
  "google calendar": ["https://calendar.google.com", "com.google.android.calendar"],
  "telegram": ["https://telegram.org", "org.telegram.messenger"],
  "whatsapp": ["https://www.whatsapp.com", "com.whatsapp"],
  "slack": ["https://slack.com", "com.Slack"],
  "notion": ["https://www.notion.so", "notion.id"],
  "trello": ["https://trello.com", "com.trello"],
  "discord": ["https://discord.com", "com.discord"],
  "airtable": ["https://airtable.com", "com.formagrid.airtable"],
  "openai": ["https://platform.openai.com/api-keys"],
  "gemini": ["https://aistudio.google.com/apikey"],
  "n8n": ["https://n8n.io"],
};

function tagsFor(post: A): string {
  if (/(^|\s)#\p{L}/u.test(String(post.body))) return "";
  const t = new Set<string>();
  const names: A = { template: "#shablon", prompt: "#prompt", site: "#sayt", app: "#ilova", video: "#video", tip: "#maslahat" };
  t.add(names[post.kind] ?? "#kontent");
  if (post.kind === "template") t.add("#n8n");
  const m = String(post.body).match(/Qaysi ilovalar:<\/b>\s*([^\n]+)/);
  for (const n of (m?.[1] ?? "").split("+")) {
    const w = n.trim().toLowerCase().replace(/[^a-z0-9]+/g, "");
    if (w && w !== "n8n" && w.length < 18 && t.size < 5) t.add("#" + w);
  }
  return "\n\n" + [...t].join(" ");
}

function safeName(t: string): string {
  const base = t.replace(/<[^>]+>/g, "").replace(/^[^:]*:\s*/, "").replace(/[^\p{L}\p{N}]+/gu, "_").replace(/^_+|_+$/g, "").slice(0, 60);
  return (base || "shablon") + ".json";
}

async function fetchWorkflowJson(sourceKey: string): Promise<string | null> {
  try {
    let url = "";
    if (sourceKey.startsWith("tpl:")) {
      url = GH_RAW + sourceKey.slice(4).split("/").map(encodeURIComponent).join("/");
    } else if (sourceKey.startsWith("n8n:")) {
      url = `https://api.n8n.io/api/templates/workflows/${sourceKey.slice(4)}`;
    } else return null;
    const r = await fetch(url, { signal: AbortSignal.timeout(15000), headers: { "user-agent": UA } });
    if (!r.ok) return null;
    const txt = await r.text();
    if (txt.length > 15 * 1024 * 1024) return null;
    let j: A = JSON.parse(txt);
    if (sourceKey.startsWith("n8n:")) j = j?.workflow?.workflow ?? j?.workflow ?? j;
    if (!j || !Array.isArray(j.nodes) || !j.nodes.length) return null;
    return JSON.stringify(j, null, 2);
  } catch (e) {
    console.error("workflow json", String(e));
    return null;
  }
}

async function extrasText(post: A): Promise<string> {
  const m = String(post.body).match(/Qaysi ilovalar:<\/b>\s*([^\n]+)/);
  const names = (m?.[1] ?? "").split("+").map((x: string) => x.trim().toLowerCase());
  const found: [string, [string, string?]][] = [];
  for (const [k, v] of Object.entries(APPS)) {
    if (names.some((n: string) => n === k || n.startsWith(k + " ") || n.includes(k))) found.push([k, v]);
  }
  const lines: string[] = [];
  const sites: string[] = [];
  const play: string[] = [];
  for (const [k, v] of found) {
    const label = k.replace(/\b\w/g, (c) => c.toUpperCase());
    sites.push(`• ${label}: ${v[0]}`);
    if (v[1]) play.push(`https://play.google.com/store/apps/details?id=${v[1]}`);
  }
  const okPlay: string[] = [];
  const checks = await Promise.all(play.map(urlOk));
  play.forEach((u, i) => { if (checks[i]) okPlay.push(u); });
  if (sites.length) lines.push("🌐 <b>Kerakli saytlar:</b>\n" + sites.join("\n"));
  if (okPlay.length) lines.push("📲 <b>Telefon uchun ilovalar (rasmiy Google Play):</b>\n" + okPlay.map((u) => `• ${u}`).join("\n"));
  lines.push(
    "⚙️ <b>n8n'ga o'rnatish (5 qadam):</b>\n" +
      "1. n8n.io'da ro'yxatdan o'ting (bepul sinov) yoki o'z serveringizga o'rnating.\n" +
      "2. Workflows → <i>Create workflow</i> → yuqoridagi ⋯ → <i>Import from file</i> → yuklangan .json faylni tanlang.\n" +
      "3. Qizil belgili tugunlarda <i>Credentials</i> tanlab, o'z hisobingizni ulang (yuqoridagi saytlardan kalit/akkaunt oling).\n" +
      "4. Pastdagi sinash tugmasi (<i>Execute/Test workflow</i>) bilan sinab ko'ring.\n" +
      "5. Ishlasa, o'ng yuqoridagi <i>Active</i> (yangi versiyalarda <i>Publish</i>) ni yoqing.\n" +
      "📖 Rasmiy qo'llanma: https://docs.n8n.io/workflows/export-import/",
  );
  return lines.join("\n\n");
}

async function sendFileAndExtras(token: string, post: A, replyTo: number): Promise<boolean> {
  const json = await fetchWorkflowJson(post.source_key);
  if (!json) return false;
  const form = new FormData();
  form.append("chat_id", String(CHANNEL_ID));
  form.append("document", new Blob([json], { type: "application/json" }), safeName(post.title ?? post.body.slice(0, 60)));
  let level = "";
  try {
    const n = JSON.parse(json).nodes.length as number;
    level = `\n📊 <b>Murakkablik:</b> ${n <= 6 ? "Oddiy" : n <= 14 ? "O'rtacha" : "Murakkab"} (${n} ta tugun)`;
  } catch { /* ignore */ }
  form.append("caption", "📥 <b>Shablon fayli (n8n JSON)</b>" + level + "\nn8n'da: Import from file orqali yuklang.");
  form.append("parse_mode", "HTML");
  form.append("reply_parameters", JSON.stringify({ message_id: replyTo, allow_sending_without_reply: true }));
  const r = await fetch(TG(token, "sendDocument"), { method: "POST", body: form });
  const j = await r.json();
  if (!j.ok) { console.error("sendDocument", JSON.stringify(j)); return false; }
  const extra = await extrasText(post);
  await new Promise((res) => setTimeout(res, 1500));
  const r2 = await fetch(TG(token, "sendMessage"), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      chat_id: CHANNEL_ID, text: extra, parse_mode: "HTML",
      link_preview_options: { is_disabled: true },
      reply_parameters: { message_id: replyTo, allow_sending_without_reply: true },
    }),
  });
  const j2 = await r2.json();
  if (!j2.ok) console.error("extras", JSON.stringify(j2));
  return true;
}

async function sendRepoZip(token: string, post: A, replyTo: number): Promise<boolean> {
  try {
    const full = String(post.source_key).slice(5);
    const r = await fetch(`https://codeload.github.com/${full}/zip/HEAD`, { redirect: "follow", signal: AbortSignal.timeout(40000), headers: { "user-agent": UA } });
    if (!r.ok) { await r.body?.cancel(); return false; }
    const buf = new Uint8Array(await r.arrayBuffer());
    if (buf.length > 19 * 1024 * 1024 || buf.length < 100) return false;
    const form = new FormData();
    form.append("chat_id", String(CHANNEL_ID));
    form.append("document", new Blob([buf], { type: "application/zip" }), full.replace("/", "_") + ".zip");
    form.append("caption", `📦 <b>${full}</b>: loyiha fayllari (zip)\n\n🧭 <b>Qanday ochiladi:</b>\n1. Zip faylni yuklab, arxivdan chiqaring (kompyuterda: o'ng tugma → Extract).\n2. README.md faylini oching, unda ishga tushirish yozilgan.\n3. Oddiy sayt shabloni bo'lsa, index.html ni brauzerda oching.\n⚠️ Litsenziyani o'qing va ishlatishdan oldin kodni tekshiring.`);
    form.append("parse_mode", "HTML");
    form.append("reply_parameters", JSON.stringify({ message_id: replyTo, allow_sending_without_reply: true }));
    const rr = await fetch(TG(token, "sendDocument"), { method: "POST", body: form });
    const j = await rr.json();
    if (!j.ok) console.error("sendRepoZip", JSON.stringify(j));
    return !!j.ok;
  } catch (e) {
    console.error("repo zip", String(e));
    return false;
  }
}

Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value");
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? Deno.env.get(k) ?? "";
    const token = get("POSTER_TOKEN");
    const cronKey = get("POSTER_CRON_KEY");
    if (!cronKey || req.headers.get("x-cron-key") !== cronKey) return new Response("forbidden", { status: 403 });
    if (!token) return new Response("no POSTER_TOKEN yet");

    if (req.headers.get("x-mode") === "backfill") {
      const { data: rows } = await sb.from("content_posts").select("*")
        .eq("status", "posted").eq("file_sent", false).not("tg_message_id", "is", null)
        .or("source_key.like.tpl:%,source_key.like.n8n:%,source_key.like.repo:%").order("id").limit(2);
      let done = 0;
      for (const p of rows ?? []) {
        const ok = String(p.source_key).startsWith("repo:")
          ? await sendRepoZip(token, p, p.tg_message_id)
          : await sendFileAndExtras(token, p, p.tg_message_id);
        await sb.from("content_posts").update({ file_sent: true }).eq("id", p.id);
        if (ok) done++;
        await new Promise((res) => setTimeout(res, 4000));
      }
      return new Response("backfill " + done + "/" + (rows?.length ?? 0));
    }

    for (let attempt = 0; attempt < 5; attempt++) {
      const { data: post, error } = await sb.rpc("claim_next_post");
      if (error) throw error;
      if (!post) {
        const { count } = await sb.from("content_posts").select("id", { count: "exact", head: true }).eq("status", "queued");
        if (!count) await alertAdmin("navbat bo'sh, yuboriladigan post qolmadi.", get);
        return new Response("queue empty");
      }

      const urls: string[] = post.check_urls ?? [];
      if (urls.length) {
        const ok = await Promise.all(urls.map(urlOk));
        if (ok.some((x) => !x)) {
          await sb.from("content_posts").update({ status: "skipped", error: "havola ishlamayapti" }).eq("id", post.id);
          continue;
        }
      }

      let r: Response;
      if (post.kind === "poll") {
        const pj = JSON.parse(post.body);
        r = await fetch(TG(token, "sendPoll"), {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ chat_id: CHANNEL_ID, question: pj.q, options: pj.o, is_anonymous: true }),
        });
      } else {
        r = await fetch(TG(token, "sendMessage"), {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            chat_id: CHANNEL_ID,
            text: post.body + tagsFor(post),
            parse_mode: "HTML",
            link_preview_options: { is_disabled: post.kind !== "video" },
          }),
        });
      }
      const j = await r.json();
      if (j.ok) {
        await sb.from("content_posts").update({
          status: "posted",
          posted_at: new Date().toISOString(),
          tg_message_id: j.result.message_id,
        }).eq("id", post.id);
        if (/^(tpl|n8n):/.test(post.source_key ?? "")) {
          await new Promise((res) => setTimeout(res, 2000));
          const ok = await sendFileAndExtras(token, post, j.result.message_id);
          await sb.from("content_posts").update({ file_sent: ok }).eq("id", post.id);
        }
        if (/^repo:/.test(post.source_key ?? "")) {
          await new Promise((res) => setTimeout(res, 2000));
          const ok = await sendRepoZip(token, post, j.result.message_id);
          await sb.from("content_posts").update({ file_sent: ok }).eq("id", post.id);
        }
        return new Response("posted " + post.id);
      }
      await sb.from("content_posts").update({ status: "failed", error: String(j.description).slice(0, 500) }).eq("id", post.id);
      await alertAdmin(`post #${post.id} yuborilmadi: ${String(j.description).slice(0, 200)}`, get);
      return new Response("failed " + post.id, { status: 500 });
    }
    return new Response("all skipped");
  } catch (e) {
    console.error("poster", String(e));
    return new Response("error", { status: 500 });
  }
});
