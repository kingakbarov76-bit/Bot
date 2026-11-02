"""Yopiq kanalga to'lov orqali kirish boti (aiogram 3 + SQLite).

Imkoniyatlar:
- Mijoz chek rasmini yuboradi, admin tugma bilan tasdiqlaydi yoki sabab bilan rad etadi
- Tasdiqlansa mijozga bir martalik kanal havolasi beriladi
- Referal: taklif qilingan odam to'lovi tasdiqlansa, taklif qilganga bonus tushadi
- Balans va pul yechish (minimal summa, har N kunda 1 marta, admin tasdig'i bilan)
"""
import asyncio
import html
import logging
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    User,
)
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------- SOZLAMALAR
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
CARD_NUMBER = re.sub(r"\D", "", os.getenv("CARD_NUMBER", ""))
CARD_OWNER = os.getenv("CARD_OWNER", "")
PRICE = int(os.getenv("PRICE", "100000"))
REF_BONUS = int(os.getenv("REF_BONUS", "10000"))
MIN_WITHDRAW = int(os.getenv("MIN_WITHDRAW", "50000"))
WITHDRAW_DAYS = int(os.getenv("WITHDRAW_DAYS", "15"))
DB_PATH = os.getenv("DB_PATH", "bot.db")

BOT_USERNAME = ""

BTN_BUY = "💳 Kanalga kirish"
BTN_BAL = "💰 Balans"
BTN_REF = "👥 Referal havolam"
BTN_WD = "💸 Pul yechish"
BTN_CANCEL = "❌ Bekor qilish"

REASONS = {
    "fake": ("🚫 Soxta chek", "Yuborgan chekingiz soxta yoki haqiqiy emas deb topildi."),
    "amount": ("💵 Summa kam", f"Chekdagi summa {PRICE:,} so'm dan kam.".replace(",", " ")),
    "unclear": ("🔍 Chek o'qilmayapti", "Chek rasmi aniq emas, o'qib bo'lmadi. Aniqroq rasm yuboring."),
    "other": ("❓ Boshqa sabab", "To'lovingiz tasdiqlanmadi. Savollaringiz bo'lsa, admin bilan bog'laning."),
}

# ------------------------------------------------------------- MA'LUMOTLAR BAZASI
db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.row_factory = sqlite3.Row
db.execute("PRAGMA journal_mode=WAL")
db.executescript(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        referrer_id INTEGER,
        balance INTEGER NOT NULL DEFAULT 0,
        earned INTEGER NOT NULL DEFAULT 0,
        paid INTEGER NOT NULL DEFAULT 0,
        bonus_given INTEGER NOT NULL DEFAULT 0,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_id TEXT,
        file_unique_id TEXT,
        kind TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        reason TEXT,
        created_at TEXT,
        decided_at TEXT
    );
    CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        card TEXT,
        amount INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT,
        decided_at TEXT
    );
    """
)
db.commit()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def money(n: int) -> str:
    return f"{int(n):,}".replace(",", " ") + " so'm"


def fmt_card(num: str) -> str:
    num = re.sub(r"\D", "", num)
    return " ".join(num[i : i + 4] for i in range(0, len(num), 4))


def get_user(uid: int):
    return db.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()


def who(row) -> str:
    if row is None:
        return "noma'lum"
    name = html.escape(row["full_name"] or "Ismsiz")
    if row["username"]:
        name += f" (@{html.escape(row['username'])})"
    return name


def register_user(tg_user: User, ref_id: int | None) -> None:
    exists = get_user(tg_user.id)
    if exists:
        db.execute(
            "UPDATE users SET username=?, full_name=? WHERE user_id=?",
            (tg_user.username, tg_user.full_name, tg_user.id),
        )
    else:
        referrer = None
        if ref_id and ref_id != tg_user.id and get_user(ref_id):
            referrer = ref_id
        db.execute(
            "INSERT INTO users (user_id, username, full_name, referrer_id, created_at) VALUES (?,?,?,?,?)",
            (tg_user.id, tg_user.username, tg_user.full_name, referrer, now()),
        )
    db.commit()


def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_BUY)],
            [KeyboardButton(text=BTN_BAL), KeyboardButton(text=BTN_REF)],
            [KeyboardButton(text=BTN_WD)],
        ],
        resize_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_CANCEL)]], resize_keyboard=True)


router = Router()


class Withdraw(StatesGroup):
    card = State()
    amount = State()


# ----------------------------------------------------------------- MIJOZ QISMI
@router.message(CommandStart())
async def cmd_start(m: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    ref = int(command.args) if command.args and command.args.isdigit() else None
    register_user(m.from_user, ref)
    await m.answer(
        "👋 <b>Xush kelibsiz!</b>\n\n"
        f"Yopiq kanalga kirish narxi: <b>{money(PRICE)}</b> (bir martalik to'lov).\n\n"
        f"👥 Do'stlaringizni taklif qilib ham pul ishlashingiz mumkin: har bir to'lov qilgan "
        f"do'stingiz uchun <b>{money(REF_BONUS)}</b>. Kursni sotib olmasangiz ham bo'ladi.\n\n"
        "Quyidagi menyudan tanlang 👇",
        reply_markup=menu_kb(),
    )


@router.message(F.text == BTN_CANCEL)
async def cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Bekor qilindi.", reply_markup=menu_kb())


@router.message(F.text == BTN_BUY)
async def buy(m: Message, state: FSMContext):
    await state.clear()
    register_user(m.from_user, None)
    u = get_user(m.from_user.id)
    if u["paid"]:
        await m.answer(
            "✅ Siz to'lov qilgansiz va kanal havolasi sizga yuborilgan. "
            "Muammo bo'lsa, admin bilan bog'laning.",
            reply_markup=menu_kb(),
        )
        return
    if db.execute(
        "SELECT 1 FROM payments WHERE user_id=? AND status='pending'", (m.from_user.id,)
    ).fetchone():
        await m.answer("⏳ Chekingiz tekshirilmoqda. Javob 24 soat ichida keladi.")
        return
    await m.answer(
        "💳 <b>To'lov ma'lumotlari</b>\n\n"
        f"Narxi: <b>{money(PRICE)}</b> (bir martalik)\n"
        f"Karta: <code>{fmt_card(CARD_NUMBER)}</code>\n"
        f"Karta egasi: <b>{html.escape(CARD_OWNER)}</b>\n\n"
        "To'lovni qilgach, <b>chek rasmini</b> shu yerga yuboring.\n"
        "To'lov 24 soat ichida tekshiriladi."
    )


@router.message(StateFilter(None), F.photo | (F.document & F.document.mime_type.startswith("image/")))
async def receipt(m: Message):
    register_user(m.from_user, None)
    u = get_user(m.from_user.id)
    if u["paid"]:
        await m.answer("✅ Siz allaqachon to'lov qilgansiz.")
        return
    if db.execute(
        "SELECT 1 FROM payments WHERE user_id=? AND status='pending'", (m.from_user.id,)
    ).fetchone():
        await m.answer("⏳ Oldingi chekingiz hali tekshirilmoqda. Iltimos, kuting.")
        return

    if m.photo:
        f = m.photo[-1]
        kind = "photo"
    else:
        f = m.document
        kind = "document"

    cur = db.execute(
        "INSERT INTO payments (user_id, file_id, file_unique_id, kind, created_at) VALUES (?,?,?,?,?)",
        (m.from_user.id, f.file_id, f.file_unique_id, kind, now()),
    )
    db.commit()
    pid = cur.lastrowid

    dup = db.execute(
        "SELECT COUNT(*) AS c FROM payments WHERE file_unique_id=? AND id!=?", (f.file_unique_id, pid)
    ).fetchone()["c"]

    caption = (
        f"🧾 <b>Yangi chek #{pid}</b>\n"
        f"👤 {who(u)}\n"
        f"🆔 <code>{m.from_user.id}</code>\n"
        f"💵 Kutilayotgan summa: {money(PRICE)}"
    )
    if u["referrer_id"] and not u["bonus_given"]:
        caption += f"\n👥 Taklif qilgan: {who(get_user(u['referrer_id']))} (tasdiqlansa +{money(REF_BONUS)})"
    if dup:
        caption += "\n\n⚠️ <b>Diqqat:</b> bu rasm oldin ham yuborilgan!"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pok:{pid}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pno:{pid}"),
            ]
        ]
    )
    try:
        if kind == "photo":
            await m.bot.send_photo(ADMIN_ID, f.file_id, caption=caption, reply_markup=kb)
        else:
            await m.bot.send_document(ADMIN_ID, f.file_id, caption=caption, reply_markup=kb)
    except Exception:
        logging.exception("Adminga chekni yuborib bo'lmadi")
        db.execute("DELETE FROM payments WHERE id=?", (pid,))
        db.commit()
        await m.answer("⚠️ Texnik xatolik. Birozdan keyin qayta urinib ko'ring.")
        return

    await m.answer("✅ Chek qabul qilindi. To'lovingiz 24 soat ichida tekshiriladi, natija shu yerga keladi.")


@router.message(F.text == BTN_BAL)
async def balance(m: Message, state: FSMContext):
    await state.clear()
    register_user(m.from_user, None)
    u = get_user(m.from_user.id)
    invited = db.execute("SELECT COUNT(*) AS c FROM users WHERE referrer_id=?", (m.from_user.id,)).fetchone()["c"]
    paid_ref = db.execute(
        "SELECT COUNT(*) AS c FROM users WHERE referrer_id=? AND bonus_given=1", (m.from_user.id,)
    ).fetchone()["c"]
    await m.answer(
        f"💰 <b>Balansingiz: {money(u['balance'])}</b>\n\n"
        f"👥 Taklif qilganlar: {invited} ta\n"
        f"✅ To'lov qilganlar: {paid_ref} ta\n"
        f"💵 Jami ishlagan: {money(u['earned'])}\n\n"
        f"Pul yechish: kamida {money(MIN_WITHDRAW)}, har {WITHDRAW_DAYS} kunda 1 marta.",
        reply_markup=menu_kb(),
    )


@router.message(F.text == BTN_REF)
async def referral(m: Message, state: FSMContext):
    await state.clear()
    register_user(m.from_user, None)
    link = f"https://t.me/{BOT_USERNAME}?start={m.from_user.id}"
    share_text = "Yopiq kanalga qo'shiling:"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Do'stlarga ulashish",
                    url=f"https://t.me/share/url?url={quote(link)}&text={quote(share_text)}",
                )
            ]
        ]
    )
    await m.answer(
        "👥 <b>Sizning referal havolangiz:</b>\n\n"
        f"{link}\n\n"
        f"Havola orqali kelgan har bir odam to'lov qilib, to'lovi tasdiqlansa, sizga "
        f"<b>{money(REF_BONUS)}</b> tushadi. Kursni sotib olmagan bo'lsangiz ham ishlay olasiz.",
        reply_markup=kb,
        disable_web_page_preview=True,
    )


# ------------------------------------------------------------------ PUL YECHISH
@router.message(F.text == BTN_WD)
async def withdraw_start(m: Message, state: FSMContext):
    await state.clear()
    register_user(m.from_user, None)
    uid = m.from_user.id
    u = get_user(uid)

    if db.execute("SELECT 1 FROM withdrawals WHERE user_id=? AND status='pending'", (uid,)).fetchone():
        await m.answer("⏳ Oldingi so'rovingiz ko'rib chiqilmoqda. Iltimos, kuting.")
        return

    last = db.execute(
        "SELECT decided_at FROM withdrawals WHERE user_id=? AND status='paid' ORDER BY id DESC LIMIT 1",
        (uid,),
    ).fetchone()
    if last:
        nxt = datetime.fromisoformat(last["decided_at"]) + timedelta(days=WITHDRAW_DAYS)
        left = nxt - datetime.now(timezone.utc)
        if left.total_seconds() > 0:
            days = int(-(-left.total_seconds() // 86400))
            tz = timezone(timedelta(hours=5))
            await m.answer(
                f"⏳ Pul yechish har {WITHDRAW_DAYS} kunda 1 marta mumkin.\n"
                f"Keyingi imkoniyat: {days} kundan keyin ({nxt.astimezone(tz):%d.%m.%Y})."
            )
            return

    if u["balance"] < MIN_WITHDRAW:
        await m.answer(
            f"❗ Pul yechish uchun balans kamida {money(MIN_WITHDRAW)} bo'lishi kerak.\n"
            f"Sizda hozir: {money(u['balance'])}"
        )
        return

    await state.set_state(Withdraw.card)
    await m.answer(
        f"💳 Pul tushirilishi kerak bo'lgan <b>karta raqamini</b> yuboring (16 xonali).\n"
        f"Balansingiz: {money(u['balance'])}",
        reply_markup=cancel_kb(),
    )


@router.message(Withdraw.card, F.text)
async def withdraw_card(m: Message, state: FSMContext):
    digits = re.sub(r"\D", "", m.text)
    if len(digits) != 16:
        await m.answer("❗ Karta raqami 16 ta raqamdan iborat bo'lishi kerak. Qayta yuboring.")
        return
    await state.update_data(card=digits)
    await state.set_state(Withdraw.amount)
    u = get_user(m.from_user.id)
    await m.answer(
        f"💵 Qancha yechmoqchisiz?\nKamida: {money(MIN_WITHDRAW)}\nEng ko'pi: {money(u['balance'])}\n\n"
        "Summani raqam bilan yozing."
    )


@router.message(Withdraw.amount, F.text)
async def withdraw_amount(m: Message, state: FSMContext):
    digits = re.sub(r"\D", "", m.text)
    if not digits:
        await m.answer("❗ Summani raqam bilan yozing. Masalan: 50000")
        return
    amount = int(digits)
    u = get_user(m.from_user.id)
    if amount < MIN_WITHDRAW:
        await m.answer(f"❗ Minimal summa: {money(MIN_WITHDRAW)}")
        return
    if amount > u["balance"]:
        await m.answer(f"❗ Balansingizda yetarli mablag' yo'q. Mavjud: {money(u['balance'])}")
        return

    data = await state.get_data()
    card = data["card"]
    cur = db.execute(
        "INSERT INTO withdrawals (user_id, card, amount, created_at) VALUES (?,?,?,?)",
        (m.from_user.id, card, amount, now()),
    )
    db.commit()
    wid = cur.lastrowid
    await state.clear()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ To'landi", callback_data=f"wok:{wid}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"wno:{wid}"),
            ]
        ]
    )
    try:
        await m.bot.send_message(
            ADMIN_ID,
            f"💸 <b>Pul yechish so'rovi #{wid}</b>\n"
            f"👤 {who(u)}\n"
            f"🆔 <code>{m.from_user.id}</code>\n"
            f"💳 Karta: <code>{fmt_card(card)}</code>\n"
            f"💵 Summa: <b>{money(amount)}</b>\n"
            f"💰 Balans: {money(u['balance'])}",
            reply_markup=kb,
        )
    except Exception:
        logging.exception("Adminga yechish so'rovini yuborib bo'lmadi")
        db.execute("DELETE FROM withdrawals WHERE id=?", (wid,))
        db.commit()
        await m.answer("⚠️ Texnik xatolik. Birozdan keyin qayta urinib ko'ring.", reply_markup=menu_kb())
        return

    await m.answer(
        "✅ So'rovingiz yuborildi. Admin to'lovni amalga oshirgach, sizga xabar keladi.",
        reply_markup=menu_kb(),
    )


# --------------------------------------------------------- ADMIN: CHEKNI KO'RIB CHIQISH
@router.callback_query(F.data.startswith("pok:"), F.from_user.id == ADMIN_ID)
async def pay_approve(cb: CallbackQuery):
    pid = int(cb.data.split(":")[1])
    # Avval "band qilamiz", shunda qayta bosilsa ikki marta ishlamaydi
    cur = db.execute(
        "UPDATE payments SET status='approved', decided_at=? WHERE id=? AND status='pending'", (now(), pid)
    )
    db.commit()
    if cur.rowcount == 0:
        await cb.answer("Bu chek allaqachon ko'rib chiqilgan.", show_alert=True)
        return
    pay = db.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone()
    uid = pay["user_id"]

    try:
        link = await cb.bot.create_chat_invite_link(CHANNEL_ID, name=f"user {uid}", member_limit=1)
    except Exception as e:
        logging.exception("Havola yaratib bo'lmadi")
        db.execute("UPDATE payments SET status='pending', decided_at=NULL WHERE id=?", (pid,))
        db.commit()
        await cb.answer("Havola yaratilmadi. Bot kanalda admin ekanini tekshiring.", show_alert=True)
        await cb.bot.send_message(ADMIN_ID, f"⚠️ Chek #{pid} uchun havola yaratilmadi:\n<code>{html.escape(str(e))}</code>")
        return

    u = get_user(uid)
    db.execute("UPDATE users SET paid=1 WHERE user_id=?", (uid,))
    ref_note = ""
    referrer = u["referrer_id"]
    if referrer and not u["bonus_given"] and get_user(referrer):
        db.execute(
            "UPDATE users SET balance=balance+?, earned=earned+? WHERE user_id=?",
            (REF_BONUS, REF_BONUS, referrer),
        )
        db.execute("UPDATE users SET bonus_given=1 WHERE user_id=?", (uid,))
        ref_note = f"\n👥 {who(get_user(referrer))} ga +{money(REF_BONUS)} qo'shildi."
    db.commit()

    sent = True
    try:
        await cb.bot.send_message(
            uid,
            "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            f"Kanalga kirish havolasi:\n{link.invite_link}\n\n"
            "⚠️ Havola <b>bir martalik</b>: faqat 1 kishi kira oladi. Boshqaga bermang.",
            disable_web_page_preview=True,
        )
    except Exception:
        sent = False
        logging.exception("Mijozga havolani yuborib bo'lmadi")
        await cb.bot.send_message(
            ADMIN_ID,
            f"⚠️ Mijozga xabar yuborilmadi (botni bloklagan bo'lishi mumkin). Havolani qo'lda yuboring:\n{link.invite_link}",
        )

    if referrer and ref_note:
        try:
            r = get_user(referrer)
            await cb.bot.send_message(
                referrer,
                f"🎉 Siz taklif qilgan do'stingiz to'lov qildi!\n"
                f"Balansingizga <b>+{money(REF_BONUS)}</b> qo'shildi.\n"
                f"Hozirgi balans: <b>{money(r['balance'])}</b>",
            )
        except Exception:
            logging.exception("Taklif qilganga xabar yuborib bo'lmadi")

    status = "✅ <b>TASDIQLANDI</b>" + ("" if sent else " (mijozga xabar bormadi!)") + ref_note
    await cb.message.edit_caption(caption=cb.message.html_text + "\n\n" + status, reply_markup=None)
    await cb.answer("Tasdiqlandi")


@router.callback_query(F.data.startswith("pno:"), F.from_user.id == ADMIN_ID)
async def pay_reject_menu(cb: CallbackQuery):
    pid = int(cb.data.split(":")[1])
    rows = [[InlineKeyboardButton(text=label, callback_data=f"pr:{pid}:{code}")] for code, (label, _) in REASONS.items()]
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"pback:{pid}")])
    await cb.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer("Rad etish sababini tanlang")


@router.callback_query(F.data.startswith("pback:"), F.from_user.id == ADMIN_ID)
async def pay_back(cb: CallbackQuery):
    pid = int(cb.data.split(":")[1])
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pok:{pid}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pno:{pid}"),
            ]
        ]
    )
    await cb.message.edit_reply_markup(reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("pr:"), F.from_user.id == ADMIN_ID)
async def pay_reject(cb: CallbackQuery):
    _, pid, code = cb.data.split(":")
    pid = int(pid)
    if code not in REASONS:
        await cb.answer("Noma'lum sabab", show_alert=True)
        return
    cur = db.execute(
        "UPDATE payments SET status='rejected', reason=?, decided_at=? WHERE id=? AND status='pending'",
        (code, now(), pid),
    )
    db.commit()
    if cur.rowcount == 0:
        await cb.answer("Bu chek allaqachon ko'rib chiqilgan.", show_alert=True)
        return
    pay = db.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone()
    label, text = REASONS[code]
    try:
        await cb.bot.send_message(
            pay["user_id"],
            f"❌ <b>Chekingiz tasdiqlanmadi</b>\n\nSabab: {text}\n\n"
            f"To'g'ri chek bilan qayta urinish uchun «{BTN_BUY}» tugmasini bosing.",
        )
    except Exception:
        logging.exception("Mijozga rad xabarini yuborib bo'lmadi")
    await cb.message.edit_caption(
        caption=cb.message.html_text + f"\n\n❌ <b>RAD ETILDI</b>: {label}", reply_markup=None
    )
    await cb.answer("Rad etildi")


# --------------------------------------------------- ADMIN: PUL YECHISHNI KO'RIB CHIQISH
@router.callback_query(F.data.startswith("wok:"), F.from_user.id == ADMIN_ID)
async def wd_paid(cb: CallbackQuery):
    wid = int(cb.data.split(":")[1])
    w = db.execute("SELECT * FROM withdrawals WHERE id=?", (wid,)).fetchone()
    if not w or w["status"] != "pending":
        await cb.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return
    u = get_user(w["user_id"])
    if u["balance"] < w["amount"]:
        await cb.answer("Mijoz balansida yetarli mablag' yo'q!", show_alert=True)
        return
    db.execute("UPDATE withdrawals SET status='paid', decided_at=? WHERE id=?", (now(), wid))
    db.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (w["amount"], w["user_id"]))
    db.commit()
    new_bal = get_user(w["user_id"])["balance"]
    try:
        await cb.bot.send_message(
            w["user_id"],
            f"✅ <b>{money(w['amount'])}</b> kartangizga o'tkazildi!\n"
            f"Yangi balans: <b>{money(new_bal)}</b>",
        )
    except Exception:
        logging.exception("Mijozga to'lov xabarini yuborib bo'lmadi")
    await cb.message.edit_text(cb.message.html_text + "\n\n✅ <b>TO'LANDI</b>", reply_markup=None)
    await cb.answer("Balansdan yechildi")


@router.callback_query(F.data.startswith("wno:"), F.from_user.id == ADMIN_ID)
async def wd_reject(cb: CallbackQuery):
    wid = int(cb.data.split(":")[1])
    cur = db.execute(
        "UPDATE withdrawals SET status='rejected', decided_at=? WHERE id=? AND status='pending'", (now(), wid)
    )
    db.commit()
    if cur.rowcount == 0:
        await cb.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return
    w = db.execute("SELECT * FROM withdrawals WHERE id=?", (wid,)).fetchone()
    try:
        await cb.bot.send_message(
            w["user_id"],
            "❌ Pul yechish so'rovingiz rad etildi. Balansingiz o'zgarmadi. "
            "Savollar bo'lsa, admin bilan bog'laning.",
        )
    except Exception:
        logging.exception("Mijozga rad xabarini yuborib bo'lmadi")
    await cb.message.edit_text(cb.message.html_text + "\n\n❌ <b>RAD ETILDI</b>", reply_markup=None)
    await cb.answer("Rad etildi")


@router.message(Command("stats"), F.from_user.id == ADMIN_ID)
async def stats(m: Message):
    def q(sql: str) -> int:
        return db.execute(sql).fetchone()[0]

    users = q("SELECT COUNT(*) FROM users")
    paid = q("SELECT COUNT(*) FROM users WHERE paid=1")
    pend_pay = q("SELECT COUNT(*) FROM payments WHERE status='pending'")
    pend_wd = q("SELECT COUNT(*) FROM withdrawals WHERE status='pending'")
    owed = q("SELECT COALESCE(SUM(balance),0) FROM users")
    paid_out = q("SELECT COALESCE(SUM(amount),0) FROM withdrawals WHERE status='paid'")
    await m.answer(
        "📊 <b>Statistika</b>\n\n"
        f"Foydalanuvchilar: {users}\n"
        f"To'lov qilganlar: {paid}\n"
        f"Kutilayotgan cheklar: {pend_pay}\n"
        f"Kutilayotgan yechishlar: {pend_wd}\n"
        f"Mijozlar balansi jami (qarzingiz): {money(owed)}\n"
        f"Chiqarib berilgan jami: {money(paid_out)}"
    )


@router.message(StateFilter(None), F.text)
async def fallback(m: Message):
    await m.answer("Menyudan tanlang 👇", reply_markup=menu_kb())


# ------------------------------------------------------------------------- ISHGA TUSHIRISH
async def main():
    global BOT_USERNAME
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or not ADMIN_ID or not CHANNEL_ID or len(CARD_NUMBER) != 16:
        raise SystemExit("❌ .env faylini to'ldiring: BOT_TOKEN, ADMIN_ID, CHANNEL_ID, CARD_NUMBER")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    BOT_USERNAME = me.username

    # Bot kanalda adminligini tekshiramiz va adminga xabar beramiz
    note = "✅ Bot ishga tushdi."
    try:
        member = await bot.get_chat_member(CHANNEL_ID, me.id)
        if member.status not in ("administrator", "creator"):
            note = "⚠️ Bot ishga tushdi, lekin kanalda admin emas! Botni kanalga admin qiling."
        elif member.status == "administrator" and not getattr(member, "can_invite_users", False):
            note = "⚠️ Botga «Foydalanuvchilarni taklif qilish» huquqini bering."
    except Exception as e:
        note = f"⚠️ Bot ishga tushdi, lekin kanalni tekshirib bo'lmadi: {html.escape(str(e))}"
    try:
        await bot.send_message(ADMIN_ID, note)
    except Exception:
        logging.warning("Adminga xabar yuborib bo'lmadi: avval botga /start bosing.")

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
