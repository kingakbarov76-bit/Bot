// drop: pullik kanalga maxsus to'plam postlarini (drop_items) navbat bilan chiqaradi.
// Fayl bo'lsa, postga "📥 Faylni olish" tugmasi qo'shiladi: bot a'zolikni tekshirib, faylni shaxsiy chatga yuboradi
// (kanalda "saqlashni cheklash" yoqilgani uchun fayl kanalning o'zida ishlamasligi mumkin).
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const CHANNEL_ID = Number(Deno.env.get("CHANNEL_ID") ?? "-1004330179807");
const BOT_USERNAME = "A1Prompt_bot";
const GH_RAW = "https://raw.githubusercontent.com/kingakbarov76-bit/bot/main/";
const UA = "Mozilla/5.0 (compatible; ContentBot/1.0)";
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const TG = (t: string, m: string) => `https://api.telegram.org/bot${t}/${m}`;

async function urlOk(url: string): Promise<boolean> {
  try {
    const r = await fetch(url, { redirect: "follow", signal: AbortSignal.timeout(12000), headers: { "user-agent": UA } });
    await r.body?.cancel();
    return r.status < 500 && r.status !== 404 && r.status !== 410;
  } catch {
    return false;
  }
}

async function postItem(token: string, it: A): Promise<A> {
  const kb = it.file_src
    ? { inline_keyboard: [[{ text: "📥 Faylni olish (botdan)", url: `https://t.me/${BOT_USERNAME}?start=f_${it.id}` }]] }
    : undefined;
  if (it.photo) {
    const img = await fetch(GH_RAW + it.photo, { signal: AbortSignal.timeout(30000), headers: { "user-agent": UA } });
    if (img.ok) {
      const buf = new Uint8Array(await img.arrayBuffer());
      const form = new FormData();
      form.append("chat_id", String(CHANNEL_ID));
      form.append("protect_content", "true");
      form.append("photo", new Blob([buf], { type: "image/jpeg" }), "preview.jpg");
      if (it.body.length <= 1000) {
        form.append("caption", it.body);
        form.append("parse_mode", "HTML");
        if (kb) form.append("reply_markup", JSON.stringify(kb));
        const j = await (await fetch(TG(token, "sendPhoto"), { method: "POST", body: form })).json();
        return j;
      }
      const j0 = await (await fetch(TG(token, "sendPhoto"), { method: "POST", body: form })).json();
      if (!j0.ok) console.error("photo", JSON.stringify(j0));
      await new Promise((r) => setTimeout(r, 1200));
    } else {
      await img.body?.cancel();
    }
  }
  const r = await fetch(TG(token, "sendMessage"), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      chat_id: CHANNEL_ID, protect_content: true, text: it.body, parse_mode: "HTML",
      link_preview_options: { is_disabled: true }, ...(kb ? { reply_markup: kb } : {}),
    }),
  });
  return await r.json();
}

Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value").in("key", ["POSTER_TOKEN", "POSTER_CRON_KEY"]);
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? "";
    if (!get("POSTER_CRON_KEY") || req.headers.get("x-cron-key") !== get("POSTER_CRON_KEY")) {
      return new Response("forbidden", { status: 403 });
    }
    const token = get("POSTER_TOKEN");
    for (let attempt = 0; attempt < 5; attempt++) {
      const { data: it, error } = await sb.rpc("claim_next_drop");
      if (error) throw error;
      if (!it || !it.id) return new Response("empty");
      const urls: string[] = it.check_urls ?? [];
      if (urls.length) {
        const ok = await Promise.all(urls.map(urlOk));
        if (ok.some((x) => !x)) {
          await sb.from("drop_items").update({ status: "skipped", error: "havola ishlamayapti: " + urls.filter((_, i) => !ok[i]).join(" ") }).eq("id", it.id);
          continue;
        }
      }
      const j = await postItem(token, it);
      if (j.ok) {
        await sb.from("drop_items").update({ status: "posted", posted_at: new Date().toISOString(), tg_message_id: j.result.message_id }).eq("id", it.id);
        return new Response("posted " + it.id);
      }
      await sb.from("drop_items").update({ status: "failed", error: String(j.description).slice(0, 400) }).eq("id", it.id);
      return new Response("failed " + it.id + " " + j.description, { status: 500 });
    }
    return new Response("all skipped");
  } catch (e) {
    console.error("drop", String(e));
    return new Response("error " + String(e), { status: 500 });
  }
});
