"""Telegram order bot: product menu -> cart -> name/phone/address -> order saved to SQLite and sent to admin.
Pure Python standard library (no pip install needed). Python 3.9+.
"""
import json, os, sqlite3, time, urllib.request, urllib.parse

TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))  # your Telegram numeric id (get it from @userinfobot)
API = f"https://api.telegram.org/bot{TOKEN}/"

# Edit your products here: id -> (name, price in UZS)
PRODUCTS = {
    "p1": ("Lavash", 32000),
    "p2": ("Burger", 35000),
    "p3": ("Hot-dog", 18000),
    "p4": ("Cola 1L", 12000),
}

db = sqlite3.connect(os.environ.get("DB_PATH", "orders.db"), check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, items TEXT, total INTEGER, name TEXT, phone TEXT, address TEXT, created REAL)")
db.commit()
carts, states, forms = {}, {}, {}


def api(method, **params):
    data = json.dumps(params).encode()
    req = urllib.request.Request(API + method, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def money(n):
    return f"{n:,}".replace(",", " ") + " so'm"


def menu_kb():
    rows = [[{"text": f"{n} - {money(p)}", "callback_data": f"add:{pid}"}] for pid, (n, p) in PRODUCTS.items()]
    rows.append([{"text": "🛒 Savat", "callback_data": "cart"}])
    return {"inline_keyboard": rows}


def cart_text(uid):
    cart = carts.get(uid, {})
    if not cart:
        return "Savat bo'sh.", 0
    lines, total = [], 0
    for pid, qty in cart.items():
        name, price = PRODUCTS[pid]
        total += price * qty
        lines.append(f"{name} x {qty} = {money(price * qty)}")
    return "\n".join(lines) + f"\n\nJami: {money(total)}", total


def handle(update, send=None):
    """Process one update. `send` lets tests replace the network call."""
    send = send or api
    if "callback_query" in update:
        q = update["callback_query"]; uid = q["from"]["id"]; data = q["data"]
        send("answerCallbackQuery", callback_query_id=q["id"])
        if data.startswith("add:"):
            pid = data[4:]
            carts.setdefault(uid, {})[pid] = carts.get(uid, {}).get(pid, 0) + 1
            send("sendMessage", chat_id=uid, text=f"✅ {PRODUCTS[pid][0]} savatga qo'shildi.", reply_markup=menu_kb())
        elif data == "cart":
            text, total = cart_text(uid)
            kb = {"inline_keyboard": [[{"text": "✅ Buyurtma berish", "callback_data": "order"}], [{"text": "🗑 Tozalash", "callback_data": "clear"}]]} if total else menu_kb()
            send("sendMessage", chat_id=uid, text=text, reply_markup=kb)
        elif data == "clear":
            carts.pop(uid, None)
            send("sendMessage", chat_id=uid, text="Savat tozalandi.", reply_markup=menu_kb())
        elif data == "order":
            states[uid] = "name"; forms[uid] = {}
            send("sendMessage", chat_id=uid, text="Ismingizni yozing:")
        return
    msg = update.get("message")
    if not msg or "text" not in msg:
        return
    uid, text = msg["from"]["id"], msg["text"].strip()
    if text == "/start":
        states.pop(uid, None)
        send("sendMessage", chat_id=uid, text="Assalomu alaykum! Menyudan tanlang:", reply_markup=menu_kb())
    elif states.get(uid) == "name":
        forms[uid]["name"] = text; states[uid] = "phone"
        send("sendMessage", chat_id=uid, text="Telefon raqamingiz (masalan, +998901234567):")
    elif states.get(uid) == "phone":
        digits = "".join(c for c in text if c.isdigit())
        if len(digits) < 9:
            send("sendMessage", chat_id=uid, text="Raqam noto'g'ri. Qayta yozing:")
            return
        forms[uid]["phone"] = text; states[uid] = "address"
        send("sendMessage", chat_id=uid, text="Manzilingiz:")
    elif states.get(uid) == "address":
        forms[uid]["address"] = text; states.pop(uid)
        items, total = cart_text(uid)
        f = forms.pop(uid)
        cur = db.execute("INSERT INTO orders (user_id, items, total, name, phone, address, created) VALUES (?,?,?,?,?,?,?)",
                         (uid, items, total, f["name"], f["phone"], f["address"], time.time()))
        db.commit(); carts.pop(uid, None)
        send("sendMessage", chat_id=uid, text=f"✅ Buyurtma #{cur.lastrowid} qabul qilindi! Tez orada bog'lanamiz.")
        if ADMIN_ID:
            send("sendMessage", chat_id=ADMIN_ID, text=f"🆕 Buyurtma #{cur.lastrowid}\n{items}\n\n👤 {f['name']}\n📞 {f['phone']}\n📍 {f['address']}")
    else:
        send("sendMessage", chat_id=uid, text="Menyudan tanlang:", reply_markup=menu_kb())


def main():
    if "PUT_YOUR" in TOKEN:
        raise SystemExit("BOT_TOKEN ni kiriting (README.md ga qarang)")
    offset = 0
    print("Bot ishga tushdi. To'xtatish: Ctrl+C")
    while True:
        try:
            res = api("getUpdates", offset=offset, timeout=50)
            for u in res.get("result", []):
                offset = u["update_id"] + 1
                handle(u)
        except Exception as e:  # network hiccups: wait and retry
            print("xato:", e); time.sleep(3)


if __name__ == "__main__":
    main()
