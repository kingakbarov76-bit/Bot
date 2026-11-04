"""Offline test: simulates a full order without internet."""
import os
os.environ["DB_PATH"] = ":memory:"; os.environ["ADMIN_ID"] = "999"
import bot
sent = []
fake = lambda method, **p: sent.append((method, p)) or {"ok": True}
cb = lambda data: {"callback_query": {"id": "1", "from": {"id": 5}, "data": data}}
msg = lambda text: {"message": {"from": {"id": 5}, "text": text}}
for u in [msg("/start"), cb("add:p1"), cb("add:p1"), cb("add:p4"), cb("cart"), cb("order"),
          msg("Ali"), msg("123"), msg("+998901234567"), msg("Toshkent, Chilonzor 5")]:
    bot.handle(u, send=fake)
texts = [p.get("text", "") for m, p in sent if m == "sendMessage"]
assert any("Jami: 76 000 so'm" in t for t in texts), texts
assert any("noto'g'ri" in t for t in texts)
assert any(p.get("chat_id") == 999 and "Buyurtma #1" in p.get("text", "") for m, p in sent)
row = bot.db.execute("SELECT name, phone, total FROM orders").fetchone()
assert row == ("Ali", "+998901234567", 76000), row
print("TEST OK: buyurtma to'liq ishladi")
