// watchdog: kanal tizimini tekshiradi va o'zi tuzatadi; adminga kunlik hisobot yuboradi.
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const BASE = Deno.env.get("SUPABASE_URL")!;
const ADMIN_ID = Number(Deno.env.get("ADMIN_ID") ?? "5306954983");
const UA = "Mozilla/5.0 (compatible; ContentBot/1.0)";
const sb = createClient(BASE, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

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

Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value");
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? "";
    const cronKey = get("POSTER_CRON_KEY");
    if (!cronKey || req.headers.get("x-cron-key") !== cronKey) return new Response("forbidden", { status: 403 });
    const url = new URL(req.url);
    const digest = url.searchParams.get("digest") === "1" || new Date().getUTCHours() === 16;
    const notes: string[] = [];
    const problems: string[] = [];
    const call = (fn: string, mode?: string) =>
      fetch(`${BASE}/functions/v1/${fn}`, {
        method: "POST",
        headers: { "x-cron-key": cronKey, "content-type": "application/json", ...(mode ? { "x-mode": mode } : {}) },
        body: "{}", signal: AbortSignal.timeout(110000),
      }).then(async (r) => (await r.text()).slice(0, 80)).catch((e) => "xato: " + String(e).slice(0, 60));

    // 1) qotib qolgan "posting" postlarni qaytaramiz
    const { data: stuck } = await sb.from("content_posts").update({ status: "queued" }).eq("status", "posting").is("tg_message_id", null).select("id");
    if (stuck?.length) notes.push(`🔧 Qotib qolgan ${stuck.length} ta post navbatga qaytarildi`);

    // 2) tezlik chegarasi/vaqtinchalik xatolar bilan yiqilganlarni qayta navbatga
    const { data: failed } = await sb.from("content_posts").select("id,error").eq("status", "failed");
    const retry = (failed ?? []).filter((f: A) => /Too Many Requests|timeout|timed out|Bad Gateway|retry after/i.test(f.error ?? "")).map((f: A) => f.id);
    if (retry.length) {
      await sb.from("content_posts").update({ status: "queued", error: null }).in("id", retry);
      notes.push(`🔧 Vaqtinchalik xato bilan to'xtagan ${retry.length} ta post qayta navbatga qo'yildi`);
    }
    const hard = (failed ?? []).filter((f: A) => !retry.includes(f.id));
    if (hard.length) problems.push(`❌ ${hard.length} ta post yuborilmadi (ID: ${hard.map((f: A) => f.id).join(", ")}): ${String(hard[0].error).slice(0, 100)}`);

    // 3) yuborilmay qolgan fayllarni qayta yuborish
    const { count: noFile } = await sb.from("content_posts").select("id", { count: "exact", head: true })
      .eq("status", "posted").eq("file_sent", false).not("tg_message_id", "is", null)
      .or("source_key.like.tpl:%,source_key.like.n8n:%,source_key.like.repo:%");
    if (noFile) { const r = await call("poster", "backfill"); notes.push(`📎 Faylsiz ${noFile} ta post uchun fayl qayta yuborildi (${r})`); }

    // 4) navbat holati
    const { data: q } = await sb.from("content_posts").select("kind").eq("status", "queued");
    const byKind: Record<string, number> = {};
    (q ?? []).forEach((r: A) => { byKind[r.kind] = (byKind[r.kind] ?? 0) + 1; });
    const total = q?.length ?? 0;
    if (total < 24) {
      const rs = await Promise.all([call("content-pro"), call("content-more"), call("content-gen")]);
      notes.push(`♻️ Navbat kamaydi (${total}), generatorlar ishga tushirildi`);
      if (rs.every((x) => x.startsWith("xato"))) problems.push("⚠️ Generatorlar ishlamadi: " + rs[0]);
    }
    // generatorlar tirikmi?
    const { data: lastAuto } = await sb.from("content_posts").select("created_at").eq("origin", "auto").order("created_at", { ascending: false }).limit(1);
    const hrs = lastAuto?.[0] ? (Date.now() - Date.parse(lastAuto[0].created_at)) / 3600000 : 999;
    if (hrs > 14) problems.push(`⚠️ Yangi kontent ${Math.round(hrs)} soatdan beri yaratilmayapti (Gemini kaliti yoki limitni tekshiring)`);

    // 5) oxirgi chiqqan postlardagi havolalar hali ishlayaptimi
    const { data: recent } = await sb.from("content_posts").select("id,title,check_urls").eq("status", "posted").not("check_urls", "is", null).order("posted_at", { ascending: false }).limit(12);
    const broken: string[] = [];
    await Promise.all((recent ?? []).map(async (p: A) => {
      for (const u of p.check_urls ?? []) if (!(await urlOk(u))) broken.push(`#${p.id} ${String(p.title).slice(0, 30)} → ${u}`);
    }));
    if (broken.length) problems.push(`🔗 Ishlamayotgan havola:\n${broken.slice(0, 5).join("\n")}`);

    // 6) kunlik statistika
    const since = new Date(Date.now() - 24 * 3600 * 1000).toISOString();
    const { count: posted24 } = await sb.from("content_posts").select("id", { count: "exact", head: true }).eq("status", "posted").gte("posted_at", since);

    const lines = [
      `📊 <b>Kanal hisoboti</b>`,
      `Oxirgi 24 soatda chiqdi: <b>${posted24 ?? 0}</b> ta post`,
      `Navbatda: <b>${total}</b> (${Object.entries(byKind).map(([k, v]) => `${k}: ${v}`).join(", ") || "bo'sh"})`,
      ...notes, ...problems,
      problems.length ? "" : "✅ Muammo topilmadi",
    ].filter(Boolean);
    if ((digest || problems.length) && get("BOT_TOKEN")) {
      await fetch(`https://api.telegram.org/bot${get("BOT_TOKEN")}/sendMessage`, {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ chat_id: ADMIN_ID, text: lines.join("\n"), parse_mode: "HTML", link_preview_options: { is_disabled: true } }),
      });
    }
    return new Response(JSON.stringify({ posted24, total, notes, problems }), { headers: { "content-type": "application/json" } });
  } catch (e) {
    console.error("watchdog", String(e));
    return new Response("error", { status: 500 });
  }
});
