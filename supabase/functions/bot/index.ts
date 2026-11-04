// Yopiq kanalga to'lov orqali kirish boti.
// Supabase Edge Function (Telegram webhook) + Postgres. Sirlar: faqat BOT_TOKEN.
import { createClient } from "npm:@supabase/supabase-js@2";

// ----------------------------------------------------------------- SOZLAMALAR
let BOT_TOKEN = Deno.env.get("BOT_TOKEN") ?? "";
const ADMIN_ID = Number(Deno.env.get("ADMIN_ID") ?? "5306954983");
const CHANNEL_ID = Number(Deno.env.get("CHANNEL_ID") ?? "-1004330179807");
const CARD_NUMBER = (Deno.env.get("CARD_NUMBER") ?? "5614681804902595").replace(/\D/g, "");
const CARD_OWNER = Deno.env.get("CARD_OWNER") ?? "Akbarov Shovkatjon";
const PRICE = Number(Deno.env.get("PRICE") ?? "100000");
const REF_BONUS_BASE = Number(Deno.env.get("REF_BONUS") ?? "10000");
const REF_BONUS_PROMO = 20000;
const PROMO_END = Date.parse("2026-12-04T23:59:59+05:00"); // aksiya: shu vaqtgacha 20 000 so'm
const promoOn = () => Date.now() < PROMO_END;
const refBonus = () => (promoOn() ? REF_BONUS_PROMO : REF_BONUS_BASE);
// Aksiya ichida: bir kishi 1000+ xaridor olib kelsa, har biri uchun 40 000 (bazada give_ref_bonus hisoblaydi)
const TIER_GOAL = 1000;
const TIER_BONUS = 40000;
const tierLine = () =>
  `🏆 Aksiya davomida ${TIER_GOAL} va undan ko'p xaridor olib kelsangiz, <b>har biri uchun ${money(TIER_BONUS)}</b> ` +
  "(avvalgilari ham qayta hisoblanadi).";
const MIN_WITHDRAW = Number(Deno.env.get("MIN_WITHDRAW") ?? "50000");
const WAIT_DAYS = Number(Deno.env.get("WITHDRAW_DAYS") ?? "15"); // botga kirgandan keyin yechish uchun kutish
const unlockDate = (u: A) => new Date(new Date(u.created_at).getTime() + WAIT_DAYS * 86400000);
const FREE_CHANNEL_URL = "https://t.me/AIPromptMasters";
const INSTAGRAM_URL = "https://instagram.com/aibiznes.uz";

const BTN_BUY = "💳 Kanalga kirish";
const BTN_BAL = "💰 Balans";
const BTN_REF = "👥 Referal havolam";
const BTN_WD = "💸 Pul yechish";
const BTN_CANCEL = "❌ Bekor qilish";

const REASONS: Record<string, [string, string]> = {
  fake: ["🚫 Soxta chek", "Yuborgan chekingiz soxta yoki haqiqiy emas deb topildi."],
  amount: ["💵 Summa kam", `Chekdagi summa ${money(PRICE)} dan kam.`],
  unclear: ["🔍 Chek o'qilmayapti", "Chek rasmi aniq emas, o'qib bo'lmadi. Aniqroq rasm yuboring."],
  other: ["❓ Boshqa sabab", "To'lovingiz tasdiqlanmadi. Savollaringiz bo'lsa, admin bilan bog'laning."],
};

// deno-lint-ignore no-explicit-any
type A = any;

const sb = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  { auth: { persistSession: false } },
);

// Token Secrets'da bo'lmasa, yopiq bot_config jadvalidan o'qiladi (faqat service_role kira oladi)
async function loadToken() {
  if (BOT_TOKEN) return;
  const { data } = await sb.from("bot_config").select("value").eq("key", "BOT_TOKEN").maybeSingle();
  BOT_TOKEN = data?.value ?? "";
}

// ------------------------------------------------------------------ YORDAMCHILAR
function money(n: number): string {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " so'm";
}
const esc = (s: unknown) =>
  String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const fmtCard = (n: string) => n.replace(/\D/g, "").replace(/(.{4})/g, "$1 ").trim();
const fmtDate = (d: Date) =>
  new Intl.DateTimeFormat("ru-RU", { timeZone: "Asia/Tashkent", day: "2-digit", month: "2-digit", year: "numeric" })
    .format(d);

async function webhookSecret(): Promise<string> {
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("wh:" + BOT_TOKEN));
  return Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function tg(method: string, body: Record<string, unknown> = {}): Promise<A> {
  const r = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const j = await r.json();
  if (!j.ok) throw new Error(`${method}: ${j.description}`);
  return j.result;
}

const send = (chat_id: number, text: string, extra: Record<string, unknown> = {}) =>
  tg("sendMessage", { chat_id, text, parse_mode: "HTML", link_preview_options: { is_disabled: true }, ...extra });

async function safeSend(chat_id: number, text: string, extra: Record<string, unknown> = {}) {
  try {
    return await send(chat_id, text, extra);
  } catch (e) {
    console.error("safeSend", chat_id, String(e));
  }
}

const menuKb = {
  keyboard: [[{ text: BTN_BUY }], [{ text: BTN_BAL }, { text: BTN_REF }], [{ text: BTN_WD }]],
  resize_keyboard: true,
};
const cancelKb = { keyboard: [[{ text: BTN_CANCEL }]], resize_keyboard: true };
const socialKb = {
  inline_keyboard: [
    [{ text: "🆓 Bepul kanal", url: FREE_CHANNEL_URL }, { text: "📸 Instagram", url: INSTAGRAM_URL }],
  ],
};

let botUsername = "";
async function getBotUsername(): Promise<string> {
  if (!botUsername) botUsername = (await tg("getMe")).username;
  return botUsername;
}

// ----------------------------------------------------------------- BAZA
async function getUser(uid: number): Promise<A> {
  const { data, error } = await sb.from("users").select("*").eq("user_id", uid).maybeSingle();
  if (error) throw error;
  return data;
}

function who(u: A): string {
  if (!u) return "noma'lum";
  let n = esc(u.full_name || "Ismsiz");
  if (u.username) n += ` (@${esc(u.username)})`;
  return n;
}

async function upsertUser(from: A, refId: number | null): Promise<A> {
  const full = [from.first_name, from.last_name].filter(Boolean).join(" ");
  const uname = from.username ?? null;
  const u = await getUser(from.id);
  if (u) {
    if (u.username !== uname || u.full_name !== full) {
      await sb.from("users").update({ username: uname, full_name: full }).eq("user_id", from.id);
    }
    return u;
  }
  let referrer: number | null = null;
  if (refId && refId !== from.id && (await getUser(refId))) referrer = refId;
  const { data, error } = await sb.from("users")
    .insert({ user_id: from.id, username: uname, full_name: full, referrer_id: referrer })
    .select().single();
  if (error) {
    const again = await getUser(from.id);
    if (again) return again;
    throw error;
  }
  return data;
}

const setState = (uid: number, state: string, data: A = null) =>
  sb.from("users").update({ state, state_data: data }).eq("user_id", uid);

// ----------------------------------------------------------------- MIJOZ QISMI
function welcomeShort(): string {
  return "👋 <b>Xush kelibsiz!</b> Bu yerda 2 ta imkoniyat bor:\n\n" +
    `👥 <b>Bonus dasturi:</b> do'stingiz yopiq kanalga obuna bo'lsa, sizga <b>${money(refBonus())}</b>` +
    (promoOn() ? " (🔥 aksiya 4-dekabrgacha)" : "") + ". Kanalni sotib olish shart emas.\n" +
    (promoOn() ? tierLine() + "\n" : "") + "\n" +
    "🔒 <b>Yopiq kanal:</b> har kuni tayyor promptlar, n8n fayllari, ilovalar va kod loyihalari.\n\n" +
    "Qaysi biri qiziq? 👇";
}
const welcomeKb = {
  inline_keyboard: [
    [{ text: "🎁 Sovg'a: 3 ta tayyor prompt", callback_data: "u:gift" }],
    [{ text: "👥 Bonus: havolamni olish", callback_data: "u:ref" }],
    [{ text: "🔒 Yopiq kanal haqida", callback_data: "u:info" }],
    [{ text: "🆓 Bepul kanal: kunlik bepul promptlar", url: FREE_CHANNEL_URL }],
  ],
};

const GIFT =
  "🎁 <b>Sovg'a: 3 ta tayyor prompt</b>\n" +
  "Matn ustiga bosing, nusxa olinadi. [ ] ichini o'zingiznikiga almashtirib, ChatGPT, Claude yoki Gemini'ga yuboring.\n\n" +
  "1️⃣ <b>Mijoz «qimmat» desa</b>\n<code>Sen tajribali sotuv menejerisan. Biznesim: [biznes turi]. Mahsulot: [nomi va narxi]. Mijoz shunday e'tiroz bildirdi: \"[e'tiroz matni]\". Menga 3 xil javob yoz: 1) yumshoq, 2) faktlarga asoslangan, 3) qisqa va do'stona. O'zbek tilida, 3-5 gap, bosimsiz, yolg'on va'dasiz.</code>\n\n" +
  "2️⃣ <b>1 haftalik post rejasi</b>\n<code>Sen ijtimoiy tarmoq mutaxassisisan. Biznesim: [biznes turi, shahar]. Auditoriya: [yosh, qiziqish]. Maqsad: [yangi mijoz jalb qilish]. 7 kunlik kontent reja tuz, jadvalda: kun, post turi, mavzu, 2 gaplik g'oya, chaqiriq. Sotuv postlari 2 tadan oshmasin.</code>\n\n" +
  "3️⃣ <b>Sotuv matni</b>\n<code>Sen reklama matnlari mutaxassisisan. Mahsulot: [nomi]. Xususiyatlari: [3-5 ta]. Narxi: [narx]. Kim uchun: [mijoz]. Telegram uchun sotuv matni yoz: sarlavha, muammo, yechim, 3 ta foyda, chaqiriq. 800 belgigacha, mubolag'asiz. 2 ta variant ber.</code>\n\n" +
  "🆓 Yana 5 ta prompt bepul kanalda (tepada qadalgan post). U yerda har kuni yangilari chiqadi.";

async function logEv(uid: number, ev: string) {
  try { await sb.from("events").insert({ user_id: uid, event: ev }); } catch (_) { /* jurnal xatosi botni to'xtatmasin */ }
}

// ----------------------------------------------------------------- KANAL FAYLLARI (drop_items)
// Kanalda "saqlashni cheklash" yoqilgan, shuning uchun fayllar a'zoga bot orqali oddiy fayl bo'lib yuboriladi.
const GH_RAW = "https://raw.githubusercontent.com/kingakbarov76-bit/bot/main/";

async function isMember(uid: number): Promise<boolean> {
  if (uid === ADMIN_ID) return true;
  try {
    const m = await tg("getChatMember", { chat_id: CHANNEL_ID, user_id: uid });
    return ["member", "administrator", "creator"].includes(m.status) || (m.status === "restricted" && m.is_member);
  } catch {
    return false;
  }
}

async function deliverFile(chat: number, it: A): Promise<A> {
  const caption = `📥 <b>${esc(it.title)}</b>\n🔒 Faqat shaxsiy foydalanish uchun.`;
  if (it.file_id) {
    try {
      return await tg("sendDocument", { chat_id: chat, document: it.file_id, caption, parse_mode: "HTML" });
    } catch (e) {
      console.error("file_id eskirgan", String(e));
    }
  }
  tg("sendChatAction", { chat_id: chat, action: "upload_document" }).catch(() => {});
  const src = String(it.file_src);
  const url = src.startsWith("gh:") ? GH_RAW + src.slice(3) : src.slice(4);
  const r = await fetch(url, { redirect: "follow", signal: AbortSignal.timeout(90000), headers: { "user-agent": "A1PromptBot/1.0" } });
  if (!r.ok) { await r.body?.cancel(); throw new Error(`yuklab bo'lmadi: ${r.status}`); }
  const buf = new Uint8Array(await r.arrayBuffer());
  if (buf.length > 49 * 1024 * 1024) throw new Error("fayl 49 MB dan katta");
  const form = new FormData();
  form.append("chat_id", String(chat));
  form.append("document", new Blob([buf]), it.file_name || "fayl");
  form.append("caption", caption);
  form.append("parse_mode", "HTML");
  const j = await (await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendDocument`, { method: "POST", body: form })).json();
  if (!j.ok) throw new Error(`sendDocument: ${j.description}`);
  const fid = j.result.document?.file_id;
  if (fid) await sb.from("drop_items").update({ file_id: fid }).eq("id", it.id);
  return j.result;
}

async function sendDropFile(uid: number, id: number) {
  await logEv(uid, "file");
  if (!(await isMember(uid))) {
    return send(uid,
      "🔒 Bu fayl faqat <b>yopiq kanal a'zolari</b> uchun.\n\nKanalda har kuni tayyor promptlar, kodlar, saytlar, shablonlar va fayllar chiqadi.",
      { reply_markup: { inline_keyboard: [[{ text: "🔒 Yopiq kanal haqida", callback_data: "u:info" }], [{ text: "💳 To'lov ma'lumotlari", callback_data: "u:pay" }]] } });
  }
  const { data: it } = await sb.from("drop_items").select("id,title,file_src,file_name,file_id").eq("id", id).maybeSingle();
  if (!it?.file_src) return send(uid, "⚠️ Fayl topilmadi. Admin bilan bog'laning.");
  try {
    await deliverFile(uid, it);
    await sb.rpc("drop_dl", { p_id: id });
  } catch (e) {
    console.error("deliver", id, String(e));
    await safeSend(ADMIN_ID, `⚠️ Fayl #${id} yuborilmadi: <code>${esc(String(e))}</code>`);
    return send(uid, "⚠️ Faylni yuborishda xatolik bo'ldi. Admin xabardor qilindi, tez orada tuzatiladi.");
  }
}

function welcomeText(): string {
  return "👋 <b>Xush kelibsiz!</b>\n\n" +
    `🔒 <b>Yopiq kanal</b> narxi: <b>${money(PRICE)}</b> (bir martalik to'lov).\n` +
    "Ichida: har kuni yangi tayyor promptlar (nusxa olib ishlatasiz), n8n shablon fayllari (import qilasiz), ilova va vosita tavsiyalari, kod loyihalari (zip).\n" +
    "Nima uchun kerak: har safar noldan yozish yoki izlash o'rniga tayyor narsani olasiz, vaqt tejaladi.\n" +
    "Kanal materiallarini ko'chirib yoki boshqaga yuborib bo'lmaydi, ular faqat a'zolar uchun.\n\n" +
    "👥 <b>Bonus dasturi:</b> «Referal havolam» tugmasidan shaxsiy havola olasiz. " +
    `Do'stingiz shu havola orqali to'lov qilsa va to'lovi tasdiqlansa, balansingizga <b>${money(refBonus())}</b> yoziladi` +
    (promoOn() ? ` (🔥 aksiya: 4-dekabrgacha 20 000 so'm, keyin ${money(REF_BONUS_BASE)}). ` + tierLine() + " " : ". ") +
    `Botga kirganingizdan ${WAIT_DAYS} kun o'tgach, istalgan vaqtda kartaga yechasiz (kamida ${money(MIN_WITHDRAW)}). ` +
    "Kanalga kirmasangiz ham qatnashsa bo'ladi.\n" +
    "⚠️ Daromad kafolatlanmaydi: u do'stlaringiz qaroriga bog'liq.";
}

const socialText =
  "💡 <b>Tavsiya:</b> obuna bo'lib turing, har kuni foydali narsalar chiqadi:\n" +
  "🆓 Bepul kanal: namunaviy promptlar va maslahatlar\n" +
  "📸 Instagram @aibiznes.uz: qisqa videolar";

async function hasPending(table: "payments" | "withdrawals", uid: number): Promise<boolean> {
  const { data } = await sb.from(table).select("id").eq("user_id", uid).eq("status", "pending").limit(1);
  return !!data?.length;
}

async function showBuy(u: A) {
  const uid = u.user_id;
  if (u.paid) {
    return send(uid, "✅ Siz to'lov qilgansiz va kanal havolasi sizga yuborilgan. Muammo bo'lsa, admin bilan bog'laning.", { reply_markup: menuKb });
  }
  if (await hasPending("payments", uid)) {
    return send(uid, "⏳ Chekingiz tekshirilmoqda. Javob 24 soat ichida keladi.");
  }
  return send(
    uid,
    "💳 <b>To'lov ma'lumotlari</b>\n\n" +
      `Narxi: <b>${money(PRICE)}</b> (bir martalik)\n` +
      `Karta: <code>${fmtCard(CARD_NUMBER)}</code>\n` +
      `Karta egasi: <b>${esc(CARD_OWNER)}</b>\n\n` +
      "To'lovni qilgach, <b>chek rasmini</b> shu yerga yuboring.\n" +
      "To'lov 24 soat ichida tekshiriladi.",
  );
}

async function receipt(u: A, m: A) {
  const uid = u.user_id;
  if (u.paid) return send(uid, "✅ Siz allaqachon to'lov qilgansiz.");
  if (await hasPending("payments", uid)) {
    return send(uid, "⏳ Oldingi chekingiz hali tekshirilmoqda. Iltimos, kuting.");
  }
  const kind = m.photo ? "photo" : "document";
  const file = m.photo ? m.photo[m.photo.length - 1] : m.document;

  const { data: pay, error } = await sb.from("payments")
    .insert({ user_id: uid, file_id: file.file_id, file_unique_id: file.file_unique_id, kind })
    .select().single();
  if (error) {
    if (error.code === "23505") return send(uid, "⏳ Oldingi chekingiz hali tekshirilmoqda. Iltimos, kuting.");
    throw error;
  }

  const { count: dup } = await sb.from("payments").select("id", { count: "exact", head: true })
    .eq("file_unique_id", file.file_unique_id).neq("id", pay.id);

  let caption = `🧾 <b>Yangi chek #${pay.id}</b>\n👤 ${who(u)}\n🆔 <code>${uid}</code>\n💵 Kutilayotgan summa: ${money(PRICE)}`;
  if (u.referrer_id && !u.bonus_given) {
    caption += `\n👥 Taklif qilgan: ${who(await getUser(u.referrer_id))} (tasdiqlansa +${money(refBonus())})`;
  }
  if (dup) caption += "\n\n⚠️ <b>Diqqat:</b> bu rasm oldin ham yuborilgan!";

  try {
    await tg(kind === "photo" ? "sendPhoto" : "sendDocument", {
      chat_id: ADMIN_ID,
      [kind]: file.file_id,
      caption,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [[
          { text: "✅ Tasdiqlash", callback_data: `pok:${pay.id}` },
          { text: "❌ Rad etish", callback_data: `pno:${pay.id}` },
        ]],
      },
    });
  } catch (e) {
    console.error("adminga chek yuborilmadi", String(e));
    await sb.from("payments").delete().eq("id", pay.id);
    return send(uid, "⚠️ Texnik xatolik. Birozdan keyin qayta urinib ko'ring.");
  }
  return send(uid, "✅ Chek qabul qilindi. To'lovingiz 24 soat ichida tekshiriladi, natija shu yerga keladi.");
}

async function showBalance(u: A) {
  const uid = u.user_id;
  const inv = await sb.from("users").select("user_id", { count: "exact", head: true }).eq("referrer_id", uid);
  const paidRef = await sb.from("users").select("user_id", { count: "exact", head: true })
    .eq("referrer_id", uid).eq("bonus_given", true);
  let tier = "";
  if (promoOn()) {
    const { data: ps } = await sb.rpc("promo_sales", { p_referrer: uid });
    const n = Number(ps ?? 0);
    tier = n >= TIER_GOAL
      ? `\n🏆 Aksiyadagi xaridorlaringiz: <b>${n}</b>. Siz ${TIER_GOAL} ga yetgansiz, har biri uchun ${money(TIER_BONUS)}.`
      : `\n🏆 Aksiyadagi xaridorlaringiz: <b>${n} / ${TIER_GOAL}</b>\n${TIER_GOAL} ga yetsangiz, hammasi ${money(TIER_BONUS)} dan qayta hisoblanadi.`;
  }
  return send(
    uid,
    `💰 <b>Balansingiz: ${money(u.balance)}</b>\n\n` +
      `👥 Taklif qilganlar: ${inv.count ?? 0} ta\n` +
      `✅ To'lov qilganlar: ${paidRef.count ?? 0} ta\n` +
      `💵 Jami ishlagan: ${money(u.earned)}\n\n` +
      (unlockDate(u).getTime() > Date.now()
        ? `🔓 Yechish ochiladi: <b>${fmtDate(unlockDate(u))}</b> (botga kirganingizdan ${WAIT_DAYS} kun o'tgach)\n`
        : "🔓 Yechish ochiq: istalgan vaqtda\n") +
      `Kamida ${money(MIN_WITHDRAW)}.` +
      (promoOn() ? `\n\n🔥 Aksiya: 4-dekabrgacha har bir do'st uchun ${money(REF_BONUS_PROMO)}.` + tier : ""),
    { reply_markup: menuKb },
  );
}

async function showReferral(u: A) {
  const link = `https://t.me/${await getBotUsername()}?start=${u.user_id}`;
  const share = `https://t.me/share/url?url=${encodeURIComponent(link)}&text=${encodeURIComponent("Yopiq kanalga qo'shiling:")}`;
  return send(
    u.user_id,
    "👥 <b>Sizning referal havolangiz:</b>\n\n" + link + "\n\n" +
      `Havola orqali kelgan har bir odam to'lov qilib, to'lovi tasdiqlansa, sizga <b>${money(refBonus())}</b> yoziladi` +
      (promoOn() ? " (🔥 aksiya 4-dekabrgacha)" : "") + ".\n" +
      (promoOn() ? tierLine() + "\n" : "") +
      `Yechish: botga kirganingizdan ${WAIT_DAYS} kun o'tgach, istalgan vaqtda, kamida ${money(MIN_WITHDRAW)}.\n` +
      "Kanalni sotib olmagan bo'lsangiz ham qatnashasiz.\n⚠️ Daromad kafolatlanmaydi: u do'stlaringiz qaroriga bog'liq.\n\n" +
      "💡 Maslahat: do'stlaringizga bepul kanaldagi foydali postlarni ham yuboring. Ular kanal qanday ekanini ko'rib, ishonch bilan qaror qiladi.",
    { reply_markup: { inline_keyboard: [[{ text: "📤 Do'stlarga ulashish", url: share }], [{ text: "🆓 Bepul kanal (ulashish uchun postlar)", url: FREE_CHANNEL_URL }]] } },
  );
}

// ------------------------------------------------------------------ PUL YECHISH
async function startWithdraw(u: A) {
  const uid = u.user_id;
  if (await hasPending("withdrawals", uid)) {
    return send(uid, "⏳ Oldingi so'rovingiz ko'rib chiqilmoqda. Iltimos, kuting.");
  }
  const left = unlockDate(u).getTime() - Date.now();
  if (left > 0) {
    return send(
      uid,
      `⏳ Pul yechish botga kirganingizdan ${WAIT_DAYS} kun o'tgach ochiladi.\n` +
        `Ochilish sanasi: ${fmtDate(unlockDate(u))} (${Math.ceil(left / 86400000)} kun qoldi). Bonuslaringiz balansda saqlanadi.`,
    );
  }
  if (u.balance < MIN_WITHDRAW) {
    return send(
      uid,
      `❗ Pul yechish uchun balans kamida ${money(MIN_WITHDRAW)} bo'lishi kerak.\nSizda hozir: ${money(u.balance)}`,
    );
  }
  await setState(uid, "wd_card");
  return send(
    uid,
    `💳 Pul tushirilishi kerak bo'lgan <b>karta raqamini</b> yuboring (16 xonali).\nBalansingiz: ${money(u.balance)}`,
    { reply_markup: cancelKb },
  );
}

async function withdrawCard(u: A, text: string) {
  const digits = text.replace(/\D/g, "");
  if (digits.length !== 16) {
    return send(u.user_id, "❗ Karta raqami 16 ta raqamdan iborat bo'lishi kerak. Qayta yuboring.");
  }
  await setState(u.user_id, "wd_amount", { card: digits });
  return send(
    u.user_id,
    `💵 Qancha yechmoqchisiz?\nKamida: ${money(MIN_WITHDRAW)}\nEng ko'pi: ${money(u.balance)}\n\nSummani raqam bilan yozing.`,
  );
}

async function withdrawAmount(u: A, text: string) {
  const uid = u.user_id;
  const digits = text.replace(/\D/g, "");
  if (!digits) return send(uid, "❗ Summani raqam bilan yozing. Masalan: 50000");
  const amount = Number(digits);
  if (amount < MIN_WITHDRAW) return send(uid, `❗ Minimal summa: ${money(MIN_WITHDRAW)}`);
  if (amount > u.balance) return send(uid, `❗ Balansingizda yetarli mablag' yo'q. Mavjud: ${money(u.balance)}`);

  const card: string = u.state_data?.card ?? "";
  if (card.length !== 16) {
    await setState(uid, "");
    return send(uid, "⚠️ Xatolik. Iltimos, «💸 Pul yechish» ni qaytadan bosing.", { reply_markup: menuKb });
  }
  const { data: w, error } = await sb.from("withdrawals").insert({ user_id: uid, card, amount }).select().single();
  if (error) {
    await setState(uid, "");
    if (error.code === "23505") return send(uid, "⏳ Oldingi so'rovingiz ko'rib chiqilmoqda.", { reply_markup: menuKb });
    throw error;
  }
  await setState(uid, "");
  try {
    await send(
      ADMIN_ID,
      `💸 <b>Pul yechish so'rovi #${w.id}</b>\n👤 ${who(u)}\n🆔 <code>${uid}</code>\n` +
        `💳 Karta: <code>${fmtCard(card)}</code>\n💵 Summa: <b>${money(amount)}</b>\n💰 Balans: ${money(u.balance)}`,
      {
        reply_markup: {
          inline_keyboard: [[
            { text: "✅ To'landi", callback_data: `wok:${w.id}` },
            { text: "❌ Rad etish", callback_data: `wno:${w.id}` },
          ]],
        },
      },
    );
  } catch (e) {
    console.error("adminga yechish yuborilmadi", String(e));
    await sb.from("withdrawals").delete().eq("id", w.id);
    return send(uid, "⚠️ Texnik xatolik. Birozdan keyin qayta urinib ko'ring.", { reply_markup: menuKb });
  }
  return send(uid, "✅ So'rovingiz yuborildi. Admin to'lovni amalga oshirgach, sizga xabar keladi.", { reply_markup: menuKb });
}

// ----------------------------------------------------------------- XABARLAR
async function cmdStats(uid: number) {
  const { data, error } = await sb.rpc("bot_stats");
  if (error) throw error;
  const revenue = Number(data.approved) * PRICE;
  const earned = Number(data.earned_total);
  const paidOut = Number(data.paid_out);
  return send(
    uid,
    "📊 <b>Daromad hisoboti</b>\n\n" +
      `✅ Tasdiqlangan to'lovlar: ${data.approved} ta\n` +
      `💵 <b>Jami tushum: ${money(revenue)}</b>\n` +
      `📅 Bugun: ${data.approved_today} ta (${money(Number(data.approved_today) * PRICE)})\n` +
      `🗓 Shu oy: ${data.approved_month} ta (${money(Number(data.approved_month) * PRICE)})\n\n` +
      `👥 Referal bonuslar (jami hisoblangan): ${money(earned)}\n` +
      `💸 Mijozlarga to'langan: ${money(paidOut)}\n` +
      `🧾 Mijozlar balansi (hali to'lanmagan qarz): ${money(Number(data.owed))}\n\n` +
      `📈 <b>Sof foyda: ${money(revenue - earned)}</b>\n` +
      "(tushum − referal bonuslar)\n" +
      `💼 Qo'lingizda qolgan pul: ${money(revenue - paidOut)}\n` +
      "(tushum − mijozlarga to'langan)\n\n" +
      `👤 Foydalanuvchilar: ${data.users}, to'lov qilganlar: ${data.paid}\n` +
      `⏳ Kutilayotgan cheklar: ${data.pending_payments}, yechishlar: ${data.pending_withdrawals}`,
  );
}

async function handleMessage(m: A) {
  if (!m.from || m.chat?.type !== "private") return;
  const uid: number = m.from.id;
  const text: string = (m.text ?? "").trim();

  let ref: number | null = null;
  if (text.startsWith("/start")) {
    const arg = text.split(/\s+/)[1];
    if (arg && /^\d+$/.test(arg)) ref = Number(arg);
    const fm = arg?.match(/^f_(\d{1,9})$/);
    if (fm) {
      await upsertUser(m.from, null);
      return sendDropFile(uid, Number(fm[1]));
    }
  }
  const u = await upsertUser(m.from, ref);

  if (text.startsWith("/start")) {
    await logEv(uid, "start");
    await setState(uid, "");
    await send(uid, welcomeShort(), { reply_markup: welcomeKb });
    return send(uid, `🆓 Avval bepul namunalarni ko'ring: ${FREE_CHANNEL_URL}\nMenyu pastda 👇`, { reply_markup: menuKb });
  }
  if (text === "/stats" && uid === ADMIN_ID) return cmdStats(uid);
  if (text === BTN_CANCEL) {
    await setState(uid, "");
    return send(uid, "Bekor qilindi.", { reply_markup: menuKb });
  }
  if (text === BTN_BUY) { await logEv(uid, "m_buy"); await setState(uid, ""); return showBuy(u); }
  if (text === BTN_BAL) { await logEv(uid, "m_bal"); await setState(uid, ""); return showBalance(u); }
  if (text === BTN_REF) { await logEv(uid, "m_ref"); await setState(uid, ""); return showReferral(u); }
  if (text === BTN_WD) { await logEv(uid, "m_wd"); await setState(uid, ""); return startWithdraw(u); }

  if (u.state === "fb_text" && text) {
    await setState(uid, "");
    await sb.from("feedback").insert({ user_id: uid, answer: "boshqa", text: text.slice(0, 1000) });
    await safeSend(ADMIN_ID, `💬 <b>Mijoz fikri</b>\n👤 ${who(u)}\n\n${esc(text.slice(0, 1000))}`);
    return send(uid, "🙏 Rahmat! Fikringiz adminga yetkazildi.", { reply_markup: menuKb });
  }
  if (u.state === "wd_card" && text) return withdrawCard(u, text);
  if (u.state === "wd_amount" && text) return withdrawAmount(u, text);

  const isImage = m.photo || (m.document?.mime_type ?? "").startsWith("image/");
  if (isImage && !u.state) { await logEv(uid, "receipt"); return receipt(u, m); }

  if (text) return send(uid, "Menyudan tanlang 👇", { reply_markup: menuKb });
}

// ----------------------------------------------------------------- MIJOZ FIKRI
const FB_LABEL: Record<string, string> = {
  narx: "Narx qimmat", ishonch: "Hali ishonmayapman", kerakmas: "Hozir kerak emas", tushunmadim: "Tushunmadim", boshqa: "Boshqa sabab",
};

async function handleFeedback(u: A, code: string) {
  if (!FB_LABEL[code]) return;
  const uid = u.user_id;
  if (code === "boshqa") {
    await setState(uid, "fb_text");
    return send(uid, "✍️ Rahmat! Sababini bitta xabar bilan yozib yuboring. Fikringizni admin o'qiydi.", { reply_markup: cancelKb });
  }
  await sb.from("feedback").insert({ user_id: uid, answer: code });
  if (code === "narx") {
    return send(uid,
      "🙏 Rahmat! Narx haqidagi fikringizni albatta hisobga olamiz.\n\n" +
        `Hozircha kanalni sotib olmasdan ham bonus dasturida qatnashishingiz mumkin: do'stingiz to'lasa, sizga <b>${money(refBonus())}</b> yoziladi.`,
      { reply_markup: { inline_keyboard: [[{ text: "👥 Bonus: havolamni olish", callback_data: "u:ref" }]] } });
  }
  if (code === "ishonch") {
    return send(uid,
      "🙏 Rahmat, ochiq aytganingiz uchun! Avval bepul kanalda namunalarni ko'ring: u yerda yopiq kanaldagi postlardan namunalar chiqadi. " +
        `Ishonch hosil qilsangiz, keyin qaror qilasiz.\n🆓 ${FREE_CHANNEL_URL}`);
  }
  if (code === "tushunmadim") {
    return send(uid, welcomeText(), {
      reply_markup: { inline_keyboard: [[{ text: "💳 To'lov ma'lumotlari", callback_data: "u:pay" }], [{ text: "👥 Bonus: havolamni olish", callback_data: "u:ref" }]] },
    });
  }
  return send(uid, "🙏 Rahmat, tushunarli! Kerak bo'lganda menyu shu yerda turadi.", { reply_markup: menuKb });
}

// ----------------------------------------------------------------- ADMIN TUGMALARI
async function handleCallback(q: A) {
  const answer = (text?: string, alert = false) =>
    tg("answerCallbackQuery", { callback_query_id: q.id, text, show_alert: alert }).catch(() => {});
  if (String(q.data ?? "").startsWith("u:")) {
    await answer();
    const u = await upsertUser(q.from, null);
    await logEv(u.user_id, String(q.data).slice(2));
    if (String(q.data).startsWith("u:fb:")) return handleFeedback(u, String(q.data).slice(5));
    if (q.data === "u:gift") {
      return send(u.user_id, GIFT, {
        reply_markup: { inline_keyboard: [[{ text: "🆓 Bepul kanalga o'tish", url: FREE_CHANNEL_URL }], [{ text: "👥 Bonus: havolamni olish", callback_data: "u:ref" }]] },
      });
    }
    if (q.data === "u:ref") return showReferral(u);
    if (q.data === "u:pay") return showBuy(u);
    if (q.data === "u:info") {
      return send(u.user_id, welcomeText(), {
        reply_markup: { inline_keyboard: [[{ text: "💳 To'lov ma'lumotlari", callback_data: "u:pay" }], [{ text: "👥 Bonus: havolamni olish", callback_data: "u:ref" }]] },
      });
    }
    return;
  }
  if (q.from.id !== ADMIN_ID) return answer("Ruxsat yo'q", true);

  const [kind, a, b] = String(q.data ?? "").split(":");
  const chat = q.message.chat.id;
  const mid = q.message.message_id;
  const editKb = (inline_keyboard: A[]) =>
    tg("editMessageReplyMarkup", { chat_id: chat, message_id: mid, reply_markup: { inline_keyboard } }).catch(() => {});
  const note = (t: string) => safeSend(chat, t, { reply_parameters: { message_id: mid } });
  const id = Number(a);

  if (kind === "pok") {
    const { data: pay } = await sb.from("payments")
      .update({ status: "approved", decided_at: new Date().toISOString() })
      .eq("id", id).eq("status", "pending").select().maybeSingle();
    if (!pay) return answer("Bu chek allaqachon ko'rib chiqilgan.", true);
    const uid: number = pay.user_id;

    let link: string;
    try {
      link = (await tg("createChatInviteLink", { chat_id: CHANNEL_ID, name: `user ${uid}`, member_limit: 1 })).invite_link;
    } catch (e) {
      await sb.from("payments").update({ status: "pending", decided_at: null }).eq("id", id);
      await note(`⚠️ Chek #${id} uchun havola yaratilmadi:\n<code>${esc(String(e))}</code>\nBot kanalda admin ekanini tekshiring.`);
      return answer("Havola yaratilmadi. Bot kanalda admin bo'lishi kerak.", true);
    }

    await sb.from("users").update({ paid: true }).eq("user_id", uid);

    let refNote = "";
    const user = await getUser(uid);
    if (user?.referrer_id) {
      const { data: flagged } = await sb.from("users").update({ bonus_given: true })
        .eq("user_id", uid).eq("bonus_given", false).select().maybeSingle();
      if (flagged) {
        const { data: rb, error: rbErr } = await sb.rpc("give_ref_bonus", {
          p_referrer: user.referrer_id, p_buyer: uid, p_base: REF_BONUS_BASE,
        });
        if (rbErr) {
          await note(`⚠️ Referal bonusi yozilmadi (#${id}): <code>${esc(rbErr.message)}</code>`);
        } else if (rb) {
          const bonus = Number(rb.amount), topup = Number(rb.topup ?? 0), cnt = Number(rb.count ?? 0);
          const r = await getUser(user.referrer_id);
          refNote = `\n👥 ${who(r)} ga +${money(bonus + topup)} qo'shildi.` +
            (rb.promo ? ` (aksiyadagi xaridorlari: ${cnt})` : "") +
            (topup > 0 ? `\n🏆 1000-xaridor! Avvalgilari 40 000 ga qayta hisoblandi: +${money(topup)}` : "");
          let msg = `🎉 Siz taklif qilgan do'stingiz to'lov qildi!\nBalansingizga <b>+${money(bonus)}</b> qo'shildi.\n`;
          if (topup > 0) {
            msg += `\n🏆 <b>Tabriklaymiz! Siz 1000-xaridorga yetdingiz.</b>\n` +
              `Avvalgi xaridorlaringiz ham 40 000 so'mdan qayta hisoblandi: <b>+${money(topup)}</b>\n` +
              "Endi har bir yangi xaridor uchun 40 000 so'm.\n";
          } else if (rb.promo && cnt < TIER_GOAL) {
            msg += `🏆 Aksiyadagi xaridorlaringiz: <b>${cnt} / ${TIER_GOAL}</b>\n`;
          }
          msg += `\nHozirgi balans: <b>${money(r.balance)}</b>`;
          await safeSend(user.referrer_id, msg);
        }
      }
    }

    const sent = await safeSend(
      uid,
      "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n" +
        `Kanalga kirish havolasi:\n${link}\n\n` +
        "⚠️ Havola <b>bir martalik</b>: faqat 1 kishi kira oladi. Boshqaga bermang.",
    );
    await editKb([]);
    if (sent) await note(`✅ <b>TASDIQLANDI</b> (#${id})${refNote}`);
    else await note(`✅ Tasdiqlandi (#${id}), lekin mijozga xabar bormadi (botni bloklagan bo'lishi mumkin). Havolani qo'lda yuboring:\n${link}${refNote}`);
    return answer("Tasdiqlandi");
  }

  if (kind === "pno") {
    const rows = Object.entries(REASONS).map(([code, [label]]) => [{ text: label, callback_data: `pr:${id}:${code}` }]);
    rows.push([{ text: "⬅️ Orqaga", callback_data: `pback:${id}` }]);
    await editKb(rows);
    return answer("Rad etish sababini tanlang");
  }

  if (kind === "pback") {
    await editKb([[
      { text: "✅ Tasdiqlash", callback_data: `pok:${id}` },
      { text: "❌ Rad etish", callback_data: `pno:${id}` },
    ]]);
    return answer();
  }

  if (kind === "pr") {
    const code = b;
    if (!REASONS[code]) return answer("Noma'lum sabab", true);
    const { data: pay } = await sb.from("payments")
      .update({ status: "rejected", reason: code, decided_at: new Date().toISOString() })
      .eq("id", id).eq("status", "pending").select().maybeSingle();
    if (!pay) return answer("Bu chek allaqachon ko'rib chiqilgan.", true);
    const [label, text] = REASONS[code];
    await safeSend(
      pay.user_id,
      `❌ <b>Chekingiz tasdiqlanmadi</b>\n\nSabab: ${text}\n\nTo'g'ri chek bilan qayta urinish uchun «${BTN_BUY}» tugmasini bosing.`,
    );
    await editKb([]);
    await note(`❌ <b>RAD ETILDI</b> (#${id}): ${label}`);
    return answer("Rad etildi");
  }

  if (kind === "wok") {
    const { data: res, error } = await sb.rpc("pay_withdrawal", { p_id: id });
    if (error) throw error;
    if (!res.ok) {
      return answer(res.reason === "balance" ? "Mijoz balansida yetarli mablag' yo'q!" : "Bu so'rov allaqachon ko'rib chiqilgan.", true);
    }
    await safeSend(
      res.user_id,
      `✅ <b>${money(Number(res.amount))}</b> kartangizga o'tkazildi!\nYangi balans: <b>${money(Number(res.balance))}</b>`,
    );
    await editKb([]);
    await note(`✅ <b>TO'LANDI</b> (#${id}). Mijoz balansi: ${money(Number(res.balance))}`);
    return answer("Balansdan yechildi");
  }

  if (kind === "wno") {
    const { data: w } = await sb.from("withdrawals")
      .update({ status: "rejected", decided_at: new Date().toISOString() })
      .eq("id", id).eq("status", "pending").select().maybeSingle();
    if (!w) return answer("Bu so'rov allaqachon ko'rib chiqilgan.", true);
    await safeSend(
      w.user_id,
      "❌ Pul yechish so'rovingiz rad etildi. Balansingiz o'zgarmadi. Savollar bo'lsa, admin bilan bog'laning.",
    );
    await editKb([]);
    await note(`❌ <b>RAD ETILDI</b> (#${id})`);
    return answer("Rad etildi");
  }

  return answer();
}

// ----------------------------------------------------------------- WEBHOOKNI O'RNATISH
async function setup(): Promise<Response> {
  if (!BOT_TOKEN) {
    return new Response("❌ BOT_TOKEN topilmadi (Secrets yoki bot_config jadvali).", { status: 500 });
  }
  const webhookUrl = `${Deno.env.get("SUPABASE_URL")}/functions/v1/bot`;
  const info = await tg("getWebhookInfo");
  const changed = info.url !== webhookUrl;
  await tg("setWebhook", {
    url: webhookUrl,
    secret_token: await webhookSecret(),
    allowed_updates: ["message", "callback_query", "my_chat_member"],
  });

  let channel = "✅ Kanal: bot admin va havola yarata oladi.";
  try {
    const me = await tg("getMe");
    const member = await tg("getChatMember", { chat_id: CHANNEL_ID, user_id: me.id });
    if (!["administrator", "creator"].includes(member.status)) {
      channel = "⚠️ Bot kanalda admin emas! Botni kanalga admin qiling.";
    } else if (member.status === "administrator" && !member.can_invite_users) {
      channel = "⚠️ Botga «Foydalanuvchilarni taklif qilish» huquqini bering.";
    }
  } catch (e) {
    channel = `⚠️ Kanalni tekshirib bo'lmadi: ${String(e)}`;
  }

  if (changed) await safeSend(ADMIN_ID, `✅ Bot ishga tushdi.\n${channel}`);
  return new Response(`✅ Webhook o'rnatildi.\n${channel}\n(Admin ID: ${ADMIN_ID}. Agar xabar kelmasa, botga avval /start bosing.)`, {
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}

Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  try {
    await loadToken();
    if (url.pathname.endsWith("/setup")) return await setup();
    if (url.pathname.endsWith("/prewarm")) {
      // Faylni oldindan sinash: adminga yuborib file_id ni saqlaydi va xabarni o'chiradi
      const { data: ck } = await sb.from("bot_config").select("value").eq("key", "POSTER_CRON_KEY").maybeSingle();
      if (!ck?.value || req.headers.get("x-cron-key") !== ck.value) return new Response("forbidden", { status: 403 });
      const id = Number(url.searchParams.get("id"));
      const { data: it } = await sb.from("drop_items").select("id,title,file_src,file_name,file_id").eq("id", id).maybeSingle();
      if (!it?.file_src) return new Response("no item");
      try {
        const msg = await deliverFile(ADMIN_ID, { ...it, file_id: null });
        await tg("deleteMessage", { chat_id: ADMIN_ID, message_id: msg.message_id }).catch(() => {});
        return new Response(`ok ${id} ${msg.document?.file_size ?? 0}`);
      } catch (e) {
        await sb.from("drop_items").update({ error: String(e).slice(0, 300) }).eq("id", id);
        return new Response(`fail ${id} ${String(e)}`, { status: 500 });
      }
    }
    if (req.method !== "POST") return new Response("ok");
    if (!BOT_TOKEN) return new Response("BOT_TOKEN yo'q", { status: 500 });
    if (req.headers.get("x-telegram-bot-api-secret-token") !== (await webhookSecret())) {
      return new Response("forbidden", { status: 403 });
    }
    const update = await req.json();
    try {
      if (update.message) await handleMessage(update.message);
      else if (update.callback_query) await handleCallback(update.callback_query);
      else if (update.my_chat_member?.chat?.type === "private") {
        // foydalanuvchi botni bloklagan/qaytarganini yozib boramiz (voronka tahlili uchun)
        const blocked = update.my_chat_member.new_chat_member?.status === "kicked";
        const cid = update.my_chat_member.chat.id;
        await sb.from("users").update(blocked ? { blocked, blocked_at: new Date().toISOString() } : { blocked }).eq("user_id", cid);
        await logEv(cid, blocked ? "block" : "unblock");
      }
    } catch (e) {
      console.error("handler error", String(e));
      const to = update.message?.from?.id;
      if (to) await safeSend(to, "⚠️ Xatolik yuz berdi. Birozdan keyin qayta urinib ko'ring.");
    }
    return new Response("ok");
  } catch (e) {
    console.error("fatal", String(e));
    return new Response("error", { status: 500 });
  }
});
