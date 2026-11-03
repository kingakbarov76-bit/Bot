// qa: kanal izoh guruhidagi savollarga dars matniga tayanib javob beradi (webhook, POSTER_TOKEN boti).
// Shaxsiy xabarlar (obuna bo'lmaganlar) mijoz botiga yo'naltiriladi.
import { createClient } from "npm:@supabase/supabase-js@2";

// deno-lint-ignore no-explicit-any
type A = any;
const GROUP = -1004455083597;
const ADMIN = 5306954983;
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const TG = (t: string, m: string) => `https://api.telegram.org/bot${t}/${m}`;
const plain = (h: string) => String(h).replace(/<[^>]+>/g, "").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/\n{3,}/g, "\n\n").trim();

async function gemini(prompt: string, key: string): Promise<A | null> {
  for (const model of ["gemini-3.5-flash-lite", "gemini-3.6-flash"]) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-goog-api-key": key },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.3, responseMimeType: "application/json", maxOutputTokens: 1200 } }),
        signal: AbortSignal.timeout(40000),
      });
      if (!r.ok) { await r.body?.cancel(); continue; }
      const j = await r.json();
      const t = (j.candidates?.[0]?.content?.parts ?? []).map((p: A) => p.text ?? "").join("").replace(/^```(?:json)?\s*/i, "").replace(/```\s*$/, "").trim();
      return JSON.parse(t);
    } catch (e) { console.error("gemini", String(e)); }
  }
  return null;
}

Deno.serve(async (req: Request) => {
  try {
    const { data } = await sb.from("bot_config").select("key,value").in("key", ["POSTER_TOKEN", "BOT_TOKEN", "GEMINI_API_KEY", "QA_SECRET"]);
    const get = (k: string) => data?.find((r: A) => r.key === k)?.value ?? "";
    const secret = get("QA_SECRET");
    if (!secret || req.headers.get("x-telegram-bot-api-secret-token") !== secret) return new Response("forbidden", { status: 403 });
    const dry = new URL(req.url).searchParams.get("dry") === "1";
    const up = await req.json();
    const token = get("POSTER_TOKEN");
    const notifyAdmin = async (text: string) => {
      if (!get("BOT_TOKEN")) return;
      await fetch(TG(get("BOT_TOKEN"), "sendMessage"), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ chat_id: ADMIN, text, disable_web_page_preview: true }) }).catch(() => {});
    };

    // bot guruhga qo'shilganda holatni yozib qo'yamiz
    if (up.my_chat_member && up.my_chat_member.chat?.id === GROUP) {
      const st = up.my_chat_member.new_chat_member?.status;
      await sb.from("bot_config").upsert({ key: "QA_ON", value: st === "administrator" ? "true" : "false" });
      await notifyAdmin(st === "administrator"
        ? "✅ Izoh guruhida savol-javob yoqildi: bot admin bo'ldi."
        : "⚠️ Bot izoh guruhida admin emas (status: " + st + "). Savollarni o'qishi uchun uni guruhda admin qiling.");
      return new Response("ok");
    }

    const m = up.message;

    // shaxsiy chat: kontent boti bilan yozishgan odamni mijoz botiga yo'naltiramiz
    if (m && m.chat?.type === "private" && m.from && !m.from.is_bot) {
      if (!dry) {
        await fetch(TG(token, "sendMessage"), {
          method: "POST", headers: { "content-type": "application/json" },
          body: JSON.stringify({
            chat_id: m.chat.id,
            text: "👋 Bu bot kanalga kontent joylaydi, shaxsiy xabarlarga javob bermaydi.\n\n🔒 Yopiq kanalga kirish, to'lov va referal dasturi uchun asosiy botga o'ting 👇\n\n📸 Instagram va 🆓 bepul kanalga ham obuna bo'ling.",
            reply_markup: { inline_keyboard: [
              [{ text: "💳 Yopiq kanalga kirish", url: "https://t.me/A1Prompt_bot" }],
              [{ text: "🆓 Bepul kanal", url: "https://t.me/AIPromptMasters" }, { text: "📸 Instagram", url: "https://instagram.com/aibiznes.uz" }],
            ] },
          }),
        }).catch(() => {});
      }
      return new Response("ok");
    }

    if (!m || m.chat?.id !== GROUP) return new Response("ok");

    // kanal posti avtomatik nusxasi: guruh xabari -> kanal xabari xaritasi
    if (m.is_automatic_forward && m.forward_origin?.type === "channel") {
      await sb.from("qa_threads").upsert({ group_msg_id: m.message_id, channel_msg_id: m.forward_origin.message_id });
      return new Response("ok");
    }
    if (m.from?.is_bot || m.sender_chat) return new Response("ok");
    const text = String(m.text ?? m.caption ?? "").trim();
    if (text.length < 4 || text.startsWith("/")) return new Response("ok");

    // qaysi post ostida?
    let channelMsg: number | null = null;
    const rf = m.reply_to_message;
    if (rf?.is_automatic_forward && rf.forward_origin?.type === "channel") channelMsg = rf.forward_origin.message_id;
    if (!channelMsg) {
      const root = m.message_thread_id ?? rf?.message_id;
      if (root) {
        const { data: th } = await sb.from("qa_threads").select("channel_msg_id").eq("group_msg_id", root).maybeSingle();
        channelMsg = th?.channel_msg_id ?? null;
      }
    }
    let post: A = null;
    if (channelMsg) {
      const { data: p } = await sb.from("content_posts").select("id,title,body,kind,track").eq("tg_message_id", channelMsg).maybeSingle();
      post = p;
    }

    // suiiste'molga qarshi: bir foydalanuvchiga soatiga 6 ta javob
    const since = new Date(Date.now() - 3600_000).toISOString();
    const { count } = await sb.from("qa_log").select("id", { count: "exact", head: true }).eq("user_id", m.from.id).gte("created_at", since);
    if ((count ?? 0) >= 6) return new Response("limit");

    const ctx = post ? `DARS/POST MATNI:\n"""${plain(post.body).slice(0, 5000)}"""` : "Post matni topilmadi: faqat umumiy, aniq bo'lgan javob ber.";
    const out = await gemini(
      `Sen "AI PromptMaster" kanalining yordamchisisan (n8n, avtomatlashtirish, dasturlash, sayt, bot, AI, biznes boshlash). O'quvchi izohda savol yozdi.\n${ctx}\n\nO'QUVCHI XABARI: """${text.slice(0, 800)}"""\n\n` +
        `Qoidalar: oddiy o'zbek tilida (lotin), qisqa (6-8 gapgacha), aniq qadamlar bilan. Avval post matniga tayan. Post matnida yo'q narsani bilmasang yoki ishonching komil bo'lmasa, to'qima: "bu postda yozilmagan, admin tekshiradi" de va adminga:true qo'y. Dastur menyusi tugma nomlarini, narx, qonun, daromad raqamlarini o'ylab topma. Daromad va'da qilma. Agar xabar savol emas (rahmat, emoji, reklama, spam) bo'lsa, javob:null qaytar. JSON: {"javob":"...yoki null","adminga":true/false}`,
      get("GEMINI_API_KEY"),
    );
    if (!out) { await notifyAdmin("⚠️ Izohdagi savolga AI javob bera olmadi (Gemini xato)."); return new Response("no ai"); }
    const answer = out.javob ? String(out.javob).trim() : "";
    const link = `https://t.me/c/${String(GROUP).replace("-100", "")}/${m.message_id}`;
    if (!answer || answer === "null") return new Response("skip");
    const msg = "🤖 AI yordamchi:\n" + answer.slice(0, 1500) + (out.adminga ? "\n\nℹ️ Bu savolni admin ham ko'rib chiqadi." : "");

    let sent = false;
    if (!dry) {
      const r = await fetch(TG(token, "sendMessage"), {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ chat_id: GROUP, text: msg, reply_parameters: { message_id: m.message_id, allow_sending_without_reply: true }, link_preview_options: { is_disabled: true } }),
      });
      const j = await r.json();
      sent = !!j.ok;
      if (!j.ok) console.error("qa send", JSON.stringify(j));
    }
    await sb.from("qa_log").insert({ user_id: m.from.id, username: m.from.username ?? m.from.first_name ?? null, post_id: post?.id ?? null, question: text.slice(0, 500), answer: answer.slice(0, 1500), escalated: !!out.adminga, sent });
    if (out.adminga) await notifyAdmin(`❓ Admin e'tiboriga: savol javobsiz yoki noaniq.\n"${text.slice(0, 200)}"\n${link}`);
    return new Response(dry ? JSON.stringify({ dry: true, post: post?.title ?? null, msg }) : "ok", { headers: { "content-type": "application/json" } });
  } catch (e) {
    console.error("qa", String(e));
    return new Response("error", { status: 200 });
  }
});
