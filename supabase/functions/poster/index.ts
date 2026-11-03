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

Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value");
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? Deno.env.get(k) ?? "";
    const token = get("POSTER_TOKEN");
    const cronKey = get("POSTER_CRON_KEY");
    if (!cronKey || req.headers.get("x-cron-key") !== cronKey) return new Response("forbidden", { status: 403 });
    if (!token) return new Response("no POSTER_TOKEN yet");

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

      const r = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          chat_id: CHANNEL_ID,
          text: post.body,
          parse_mode: "HTML",
          link_preview_options: { is_disabled: post.kind !== "video" },
        }),
      });
      const j = await r.json();
      if (j.ok) {
        await sb.from("content_posts").update({
          status: "posted",
          posted_at: new Date().toISOString(),
          tg_message_id: j.result.message_id,
        }).eq("id", post.id);
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
