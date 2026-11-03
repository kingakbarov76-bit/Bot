// Ochiq (bepul) kanalga namuna postlar: pullik kanaldagi postlardan, oxirida botga yo'naltiruvchi tugma bilan.
// FREE_CHANNEL_ID bot_config'da bo'lmasa hech narsa qilmaydi. ?dry=1 yubormaydi, faqat ko'rsatadi.
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const TG = (t: string, m: string) => `https://api.telegram.org/bot${t}/${m}`;

function plain(h: string): string {
  return h.replace(/<br\s*\/?>/gi, "\n").replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();
}

const FOOT = "\n\n🔒 Yopiq kanalda har kuni yangi promptlar, n8n shablon fayllari, darslar va kod loyihalari.\n👉 Kirish: @A1Prompt_bot";

Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value");
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? "";
    if (!get("POSTER_CRON_KEY") || req.headers.get("x-cron-key") !== get("POSTER_CRON_KEY")) return new Response("forbidden", { status: 403 });
    const dry = new URL(req.url).searchParams.get("dry") === "1";
    const chat = get("FREE_CHANNEL_ID").trim();
    const token = get("POSTER_TOKEN");
    if (!chat && !dry) return new Response("no FREE_CHANNEL_ID yet");

    // har 3-chi post: fayl/yo'riqnoma bor mavzulardan qisqa tizer, qolganlari: to'liq namuna (prompt, maslahat)
    const n = Number(get("TEASER_N") || "0");
    const teaserTurn = n % 3 === 2;
    const kinds = teaserTurn ? ["template", "app", "site", "guide"] : ["prompt", "tip"];
    let { data: rows } = await sb.from("content_posts").select("id,kind,body,title")
      .eq("status", "posted").eq("teased", false).in("kind", kinds).order("id").limit(1);
    if (!rows?.length) {
      ({ data: rows } = await sb.from("content_posts").select("id,kind,body,title")
        .eq("status", "posted").eq("teased", false).in("kind", ["prompt", "tip", "template", "app", "site", "guide"]).order("id").limit(1));
    }
    const p = rows?.[0];
    if (!p) return new Response("nothing to tease");

    let text = plain(String(p.body));
    if (teaserTurn || ["template", "app", "site", "guide"].includes(p.kind)) {
      text = text.length > 320 ? text.slice(0, 320).replace(/\s+\S*$/, "") + "…" : text;
      text += "\n\n(To'liq matn, fayl va yo'riqnoma yopiq kanalda.)";
    } else if (text.length > 3300) {
      text = text.slice(0, 3300).replace(/\s+\S*$/, "") + "…";
    }
    text += FOOT;
    if (dry) return new Response(JSON.stringify({ id: p.id, kind: p.kind, text }, null, 1), { headers: { "content-type": "application/json" } });

    const r = await fetch(TG(token, "sendMessage"), {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({
        chat_id: chat, text, link_preview_options: { is_disabled: true },
        reply_markup: { inline_keyboard: [[{ text: "🔓 Yopiq kanalga kirish", url: "https://t.me/A1Prompt_bot" }]] },
      }),
    });
    const j = await r.json();
    if (!j.ok) { console.error("teaser", JSON.stringify(j)); return new Response("failed " + String(j.description), { status: 500 }); }
    await sb.from("content_posts").update({ teased: true }).eq("id", p.id);
    await sb.from("bot_config").upsert({ key: "TEASER_N", value: String(n + 1) });
    return new Response("teased " + p.id);
  } catch (e) {
    console.error("teaser", String(e));
    return new Response("error", { status: 500 });
  }
});
