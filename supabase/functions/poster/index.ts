// Kanalga kontent yuboruvchi funksiya. Rejalashtirish (pg_cron) uni kuniga 10 marta chaqiradi.
// Har chaqiruvda navbatdagi "queued" postni kanalga yuboradi.
import { createClient } from "npm:@supabase/supabase-js@2";

const CHANNEL_ID = Number(Deno.env.get("CHANNEL_ID") ?? "-1004330179807");
const sb = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  { auth: { persistSession: false } },
);

Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value").in("key", ["POSTER_TOKEN", "POSTER_CRON_KEY"]);
    const get = (k: string) => cfg?.find((r: { key: string }) => r.key === k)?.value ?? Deno.env.get(k) ?? "";
    const token = get("POSTER_TOKEN");
    const cronKey = get("POSTER_CRON_KEY");
    if (!cronKey || req.headers.get("x-cron-key") !== cronKey) return new Response("forbidden", { status: 403 });
    if (!token) return new Response("no POSTER_TOKEN yet");

    const { data: post, error } = await sb.rpc("claim_next_post");
    if (error) throw error;
    if (!post) return new Response("queue empty");

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
    return new Response("failed " + post.id, { status: 500 });
  } catch (e) {
    console.error("poster", String(e));
    return new Response("error", { status: 500 });
  }
});
