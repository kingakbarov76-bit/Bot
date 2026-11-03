// Kanal uchun qo'shimcha post turlari: kun maslahati (Gemini) va so'rovnomalar (tayyor ro'yxat).
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

const POLLS: [string, string[]][] = [
  ["Biznesingizda eng ko'p vaqtni nima olyapti?", ["Mijozlarga javob yozish", "Hisob-kitob / jadvallar", "Reklama va kontent", "Buyurtmalarni yuritish"]],
  ["Avtomatlashtirishni qaysi sohadan boshlagan bo'lardingiz?", ["Mijozlar bilan aloqa", "Sotuv va buyurtmalar", "Hisobot va hisob-kitob", "Kontent va reklama"]],
  ["Sun'iy intellektdan (ChatGPT, Gemini va h.k.) qanchalik foydalanasiz?", ["Har kuni", "Haftada bir necha marta", "Kam-kam", "Hali boshlamadim"]],
  ["n8n bilan avval ishlaganmisiz?", ["Ha, doim ishlataman", "Sinab ko'rganman", "Eshitganman, ishlatmaganman", "Yo'q, birinchi marta eshitaman"]],
  ["Kanalda qaysi turdagi postlar ko'proq kerak?", ["n8n shablonlar (fayl bilan)", "Tayyor promptlar", "Ilova va saytlar", "Video darsliklar"]],
  ["Biznesingiz qaysi ijtimoiy tarmoqda mijoz topadi?", ["Telegram", "Instagram", "Facebook", "Boshqa / offlayn"]],
  ["Mijozlarga qancha tez javob berasiz?", ["Bir necha daqiqada", "Bir soat ichida", "Kun davomida", "Ba'zan kechikadi"]],
  ["Hisob-kitobni qayerda yuritasiz?", ["Google Sheets / Excel", "Maxsus dastur", "Daftarda", "Hali tizim yo'q"]],
  ["Telegram bot sizning biznesingizga kerakmi?", ["Ha, juda kerak", "Balki, o'ylab ko'raman", "Hozircha yo'q", "Allaqachon bor"]],
  ["Kanaldagi shablonlarni o'zingiz o'rnata olasizmi?", ["Ha, qiynalmayman", "Yo'riqnoma bilan ha", "Yordam kerak bo'ladi", "Hali sinab ko'rmadim"]],
];

async function gemini(prompt: string, key: string): Promise<A | null> {
  for (const model of ["gemini-3.5-flash-lite", "gemini-3.6-flash"]) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": key },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.7, responseMimeType: "application/json", maxOutputTokens: 3000 },
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

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9Ѐ-ӿ]+/g, "-").slice(0, 50);

Deno.serve(async (req: Request) => {
  try {
    const { data: cfg } = await sb.from("bot_config").select("key,value").in("key", ["POSTER_CRON_KEY", "GEMINI_API_KEY", "AUTO_APPROVE"]);
    const get = (k: string) => cfg?.find((r: A) => r.key === k)?.value ?? "";
    if (!get("POSTER_CRON_KEY") || req.headers.get("x-cron-key") !== get("POSTER_CRON_KEY")) return new Response("forbidden", { status: 403 });
    const status = get("AUTO_APPROVE") === "true" ? "queued" : "draft";
    const { data: mx } = await sb.from("content_posts").select("sort_order").order("sort_order", { ascending: false }).limit(1);
    let order = (mx?.[0]?.sort_order ?? 0) + 1;
    const made: string[] = [];
    const newIds: number[] = [];

    // 1) bitta so'rovnoma (hali ishlatilmagan birinchisi)
    const { data: usedPolls } = await sb.from("content_posts").select("source_key").like("source_key", "poll:%");
    const usedSet = new Set((usedPolls ?? []).map((r: A) => r.source_key));
    for (let i = 0; i < POLLS.length; i++) {
      const k = `poll:${i}`;
      if (usedSet.has(k)) continue;
      const [q, o] = POLLS[i];
      const { data: ins, error } = await sb.from("content_posts").insert({
        sort_order: order++, kind: "poll", title: q, body: JSON.stringify({ q, o }), status, source_key: k, origin: "auto",
      }).select("id").single();
      if (!error) { made.push(k); newIds.push(ins.id); }
      break;
    }

    // 2) 3 ta maslahat (Gemini)
    const key = get("GEMINI_API_KEY");
    if (key) {
      const { data: old } = await sb.from("content_posts").select("title").eq("kind", "tip").order("id", { ascending: false }).limit(60);
      const avoid = (old ?? []).map((r: A) => r.title).join("; ");
      const out = await gemini(
        "Sen O'zbekistondagi kichik biznes egalariga sun'iy intellekt va avtomatlashtirish bo'yicha amaliy maslahat yozadigan muharrirsan. " +
          "O'zbek tilida (lotin yozuvi) 3 ta BIR-BIRIGA O'XSHAMAYDIGAN qisqa maslahat yoz. Har biri: aniq, bugunoq qo'llasa bo'ladigan, 3-5 qisqa gap, " +
          "ixtiyoriy 1-2 qadamli mini-ro'yxat. QOIDALAR: daromad va'da qilma; aniq raqam/statistika to'qima; narx yoki tarif nomlarini aytma; " +
          "mavjud bo'lmagan funksiyalarni o'ylab topma; faqat umumiy, tekshirsa bo'ladigan amaliy tavsiya. Mavzular: mijozga tez javob, jadvallarda hisob, " +
          "promptni to'g'ri yozish, takroriy ishni avtomatlashtirish, ma'lumotni zaxiralash, xavfsizlik (parol, kalit). " +
          (avoid ? `Quyidagi mavzularni takrorlama: ${avoid}. ` : "") +
          'Faqat JSON qaytar: {"tips":[{"sarlavha":"...","matn":"..."}]}',
        key,
      );
      for (const t of out?.tips ?? []) {
        const title = String(t?.sarlavha ?? "").trim().slice(0, 90);
        const text = String(t?.matn ?? "").trim();
        if (!title || text.length < 60 || text.length > 1200) continue;
        const k = `tip:${slug(title)}`;
        const body = `💡 <b>MASLAHAT: ${esc(title)}</b>\n\n${esc(text)}`;
        const { data: ins, error } = await sb.from("content_posts").insert({
          sort_order: order++, kind: "tip", title, body, status, source_key: k, origin: "auto",
        }).select("id").single();
        if (!error) { made.push(k); newIds.push(ins.id); }
      }
    }

    // Yangi maslahat/so'rovnomalarni navbat bo'ylab tarqatamiz (har 3 ta oddiy postdan keyin bittadan)
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
        if ((i + 1) % 3 === 0 && fi < fresh.length) seq.push(fresh[fi++].id);
      });
      while (fi < fresh.length) seq.push(fresh[fi++].id);
      for (let i = 0; i < seq.length; i++) await sb.from("content_posts").update({ sort_order: base + i }).eq("id", seq[i]);
    }
    return new Response(JSON.stringify({ made }), { headers: { "content-type": "application/json" } });
  } catch (e) {
    console.error("content-extra", String(e));
    return new Response("error", { status: 500 });
  }
});
