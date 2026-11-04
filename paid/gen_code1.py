# Kod loyihalari 1-5 (Python). Har biri: kod (inglizcha), README.md (o'zbekcha), test.
import os, textwrap
B = "/home/claude/bot/paid/src"
def w(path, s):
    p = os.path.join(B, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(textwrap.dedent(s).lstrip("\n"))

# ---------------------------------------------------------------- C1: Telegram buyurtma bot (stdlib)
w("telegram-buyurtma-bot/bot.py", '''
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
    return "\\n".join(lines) + f"\\n\\nJami: {money(total)}", total


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
            send("sendMessage", chat_id=ADMIN_ID, text=f"🆕 Buyurtma #{cur.lastrowid}\\n{items}\\n\\n👤 {f['name']}\\n📞 {f['phone']}\\n📍 {f['address']}")
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
''')
w("telegram-buyurtma-bot/test_bot.py", '''
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
''')
w("telegram-buyurtma-bot/README.md", '''
# Telegram buyurtma bot (Python, kutubxonasiz)

Kafe, do'kon yoki xizmat uchun oddiy buyurtma bot: menyu → savat → ism, telefon, manzil → buyurtma bazaga yoziladi va sizga (adminga) keladi.

## Kerak bo'ladi
- Python 3.9 yoki yangi (python.org dan o'rnating)
- Hech qanday qo'shimcha kutubxona kerak emas

## Ishga tushirish
1. Telegram'da @BotFather → /newbot → bot yarating va **token** oling.
2. @userinfobot ga yozib, o'zingizning **ID** raqamingizni bilib oling.
3. `bot.py` ichida `PRODUCTS` ro'yxatini o'z mahsulotlaringizga almashtiring.
4. Terminalda (Windows: PowerShell):
   - Windows: `set BOT_TOKEN=token` va `set ADMIN_ID=123456`, keyin `python bot.py`
   - Mac/Linux: `BOT_TOKEN=token ADMIN_ID=123456 python3 bot.py`
5. Botga /start yozing.

## Sinab ko'rish (internetsiz)
`python test_bot.py` → "TEST OK" chiqsa, hammasi ishlaydi.

## Buyurtmalar qayerda?
`orders.db` faylida (SQLite). DB Browser for SQLite dasturi bilan ochsangiz bo'ladi.

## Doim ishlab turishi uchun
Kompyuter o'chsa bot ham to'xtaydi. 24/7 uchun arzon VPS yoki PythonAnywhere, Railway kabi xizmatlarga joylang.
''')

# ---------------------------------------------------------------- C2: CSV -> Excel hisobot
w("excel-hisobot/report.py", '''
"""Turn a sales CSV into a formatted Excel report with summaries and a chart.
Usage: python report.py sales.csv report.xlsx
CSV columns: date (YYYY-MM-DD), product, quantity, price
"""
import csv, sys
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEAD = PatternFill("solid", fgColor="1F4E78")
WHITE = Font(bold=True, color="FFFFFF")


def style_header(ws, row=1):
    for c in ws[row]:
        c.fill, c.font, c.alignment = HEAD, WHITE, Alignment(horizontal="center")


def autosize(ws):
    for col in ws.columns:
        width = max(len(str(c.value or "")) for c in col) + 3
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(width, 40)


def build(src, dst):
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    wb = Workbook()
    ws = wb.active; ws.title = "Ma'lumot"
    ws.append(["Sana", "Mahsulot", "Soni", "Narxi", "Summa"])
    for i, r in enumerate(rows, start=2):
        ws.append([r["date"], r["product"], int(r["quantity"]), int(r["price"]), f"=C{i}*D{i}"])
    style_header(ws); autosize(ws)
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=5):
        for c in row:
            c.number_format = "#,##0"

    by_product, by_month = defaultdict(int), defaultdict(int)
    for r in rows:
        s = int(r["quantity"]) * int(r["price"])
        by_product[r["product"]] += s
        by_month[r["date"][:7]] += s

    sp = wb.create_sheet("Mahsulotlar")
    sp.append(["Mahsulot", "Tushum"])
    for k, v in sorted(by_product.items(), key=lambda x: -x[1]):
        sp.append([k, v])
    sp.append(["JAMI", f"=SUM(B2:B{sp.max_row})"])
    sp.cell(sp.max_row, 1).font = Font(bold=True)
    style_header(sp); autosize(sp)
    for c in sp["B"][1:]:
        c.number_format = "#,##0"
    ch = BarChart(); ch.title = "Mahsulotlar bo'yicha tushum"; ch.height, ch.width = 8, 16
    ch.add_data(Reference(sp, min_col=2, min_row=1, max_row=sp.max_row - 1), titles_from_data=True)
    ch.set_categories(Reference(sp, min_col=1, min_row=2, max_row=sp.max_row - 1))
    sp.add_chart(ch, "D2")

    sm = wb.create_sheet("Oylar")
    sm.append(["Oy", "Tushum"])
    for k in sorted(by_month):
        sm.append([k, by_month[k]])
    style_header(sm); autosize(sm)
    wb.save(dst)
    return sum(by_product.values())


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "sales.csv"
    dst = sys.argv[2] if len(sys.argv) > 2 else "report.xlsx"
    total = build(src, dst)
    print(f"Tayyor: {dst} (jami tushum: {total:,})")
''')
import random
random.seed(7)
prods = [("Choy", 12000), ("Qahva", 18000), ("Somsa", 7000), ("Lavash", 30000), ("Pishiriq", 9000)]
lines = ["date,product,quantity,price"]
for d in range(1, 61):
    m, day = (9 if d <= 30 else 10), (d if d <= 30 else d - 30)
    for _ in range(3):
        p, pr = random.choice(prods)
        lines.append(f"2026-{m:02d}-{day:02d},{p},{random.randint(1, 12)},{pr}")
w("excel-hisobot/sales.csv", "\n".join(lines) + "\n")
w("excel-hisobot/README.md", '''
# CSV → chiroyli Excel hisobot (grafik bilan)

Kassadan, marketpleysdan yoki Google Sheets'dan olingan sotuv ro'yxatini (CSV) 1 soniyada tayyor hisobotga aylantiradi:
- «Ma'lumot» varag'i: formulali jadval
- «Mahsulotlar» varag'i: har bir mahsulot tushumi + ustunli grafik
- «Oylar» varag'i: oyma-oy tushum

## O'rnatish
```
pip install openpyxl
```

## Ishlatish
```
python report.py sales.csv report.xlsx
```
`sales.csv` namunasi papkada bor. O'z faylingizda ustunlar shunday bo'lsin: `date,product,quantity,price` (sana YYYY-MM-DD ko'rinishida).

💡 Google Sheets'dan: Fayl → Yuklab olish → CSV.
''')

# ---------------------------------------------------------------- C3: rasmlarni ommaviy ishlash
w("rasm-ommaviy/images.py", '''
"""Batch image tool: resize, add a text watermark and convert (JPG/PNG/WEBP) every image in a folder.
Usage: python images.py INPUT_DIR OUTPUT_DIR --width 1080 --watermark "@mybrand" --format webp
"""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageOps

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def load_font(size):
    for name in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def process(path, out_dir, width, mark, fmt, quality):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if mark:
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        font = load_font(max(18, im.width // 28))
        box = d.textbbox((0, 0), mark, font=font)
        tw, th = box[2] - box[0], box[3] - box[1]
        x, y = im.width - tw - im.width // 40, im.height - th - im.height // 30
        d.text((x + 2, y + 2), mark, font=font, fill=(0, 0, 0, 110))
        d.text((x, y), mark, font=font, fill=(255, 255, 255, 190))
        im = Image.alpha_composite(im, layer)
    out = out_dir / (path.stem + "." + fmt)
    if fmt in ("jpg", "jpeg"):
        im.convert("RGB").save(out, "JPEG", quality=quality, optimize=True)
    elif fmt == "webp":
        im.save(out, "WEBP", quality=quality)
    else:
        im.save(out, "PNG", optimize=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--watermark", default="")
    ap.add_argument("--format", default="jpg", choices=["jpg", "png", "webp"])
    ap.add_argument("--quality", type=int, default=85)
    a = ap.parse_args()
    out = pathlib.Path(a.output); out.mkdir(parents=True, exist_ok=True)
    files = [p for p in sorted(pathlib.Path(a.input).iterdir()) if p.suffix.lower() in EXT]
    for p in files:
        r = process(p, out, a.width, a.watermark, a.format, a.quality)
        print("✓", r.name)
    print(f"Tayyor: {len(files)} ta rasm → {out}")


if __name__ == "__main__":
    main()
''')
w("rasm-ommaviy/README.md", '''
# Rasmlarni ommaviy kichraytirish + logo yozuvi + format o'zgartirish

Yuzlab mahsulot rasmini bir buyruq bilan:
- kerakli kenglikka kichraytiradi (masalan 1080 px, Instagram uchun),
- burchagiga brend yozuvini (watermark) qo'shadi,
- JPG / PNG / WEBP ga aylantiradi (WEBP sayt uchun 3 baravar yengil).

## O'rnatish
```
pip install pillow
```

## Ishlatish
```
python images.py rasmlar natija --width 1080 --watermark "@dokonim" --format jpg
```
- `rasmlar` - asl rasmlar papkasi
- `natija` - tayyor rasmlar shu yerga tushadi (asl rasmlar o'zgarmaydi)
- `--quality 85` - sifat (60-95)
''')

# ---------------------------------------------------------------- C4: PDF vositalari
w("pdf-vositalar/pdftool.py", '''
"""PDF toolbox: merge, split, extract pages, rotate, protect with password, show info.
Examples:
  python pdftool.py merge out.pdf a.pdf b.pdf c.pdf
  python pdftool.py split book.pdf parts/
  python pdftool.py extract book.pdf 3-7,10 out.pdf
  python pdftool.py rotate scan.pdf 90 out.pdf
  python pdftool.py protect doc.pdf secret123 out.pdf
  python pdftool.py info doc.pdf
"""
import pathlib, sys
from pypdf import PdfReader, PdfWriter


def pages_from_spec(spec, n):
    result = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-"); result += list(range(int(a), int(b) + 1))
        else:
            result.append(int(part))
    bad = [p for p in result if p < 1 or p > n]
    if bad:
        raise SystemExit(f"Bunday sahifa yo'q: {bad} (jami {n} sahifa)")
    return [p - 1 for p in result]


def merge(out, *files):
    w = PdfWriter()
    for f in files:
        for p in PdfReader(f).pages:
            w.add_page(p)
    w.write(out); print(f"Birlashtirildi: {out}")


def split(src, folder):
    d = pathlib.Path(folder); d.mkdir(parents=True, exist_ok=True)
    r = PdfReader(src)
    for i, p in enumerate(r.pages, 1):
        w = PdfWriter(); w.add_page(p); w.write(d / f"page_{i:03d}.pdf")
    print(f"{len(r.pages)} ta faylga bo'lindi: {d}")


def extract(src, spec, out):
    r = PdfReader(src); w = PdfWriter()
    for i in pages_from_spec(spec, len(r.pages)):
        w.add_page(r.pages[i])
    w.write(out); print(f"Ajratildi: {out}")


def rotate(src, deg, out):
    r = PdfReader(src); w = PdfWriter()
    for p in r.pages:
        w.add_page(p.rotate(int(deg)))
    w.write(out); print(f"Aylantirildi: {out}")


def protect(src, password, out):
    r = PdfReader(src); w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    w.encrypt(password, algorithm="AES-256")
    w.write(out); print(f"Parol qo'yildi: {out}")


def info(src, password=""):
    r = PdfReader(src)
    if r.is_encrypted:
        if not password or not r.decrypt(password):
            print("Fayl parol bilan himoyalangan. Ko'rish uchun: python pdftool.py info fayl.pdf PAROL"); return
    print(f"Sahifalar: {len(r.pages)}; shifrlangan: {r.is_encrypted}; meta: {dict(r.metadata or {})}")


if __name__ == "__main__":
    cmds = {"merge": merge, "split": split, "extract": extract, "rotate": rotate, "protect": protect, "info": info}
    if len(sys.argv) < 3 or sys.argv[1] not in cmds:
        print(__doc__); sys.exit(1)
    cmds[sys.argv[1]](*sys.argv[2:])
''')
w("pdf-vositalar/README.md", '''
# PDF vositalari: birlashtirish, bo'lish, sahifa ajratish, aylantirish, parol

Onlayn saytlarga hujjat yuklamasdan (maxfiylik!), o'z kompyuteringizda PDF bilan ishlash.

## O'rnatish
```
pip install pypdf cryptography
```

## Buyruqlar
| Vazifa | Buyruq |
|---|---|
| Bir nechta PDF'ni bitta qilish | `python pdftool.py merge natija.pdf 1.pdf 2.pdf` |
| Har sahifani alohida faylga | `python pdftool.py split kitob.pdf sahifalar/` |
| Kerakli sahifalarni olish | `python pdftool.py extract kitob.pdf 3-7,10 qism.pdf` |
| Aylantirish (90/180/270) | `python pdftool.py rotate skan.pdf 90 tuzatilgan.pdf` |
| Parol qo'yish | `python pdftool.py protect hujjat.pdf parol123 himoyali.pdf` |
| Ma'lumot | `python pdftool.py info hujjat.pdf` |
''')

# ---------------------------------------------------------------- C5: hisob-faktura PDF
w("hisob-faktura-pdf/invoice.py", '''
"""Generate a clean invoice PDF from a JSON file.
Usage: python invoice.py invoice.json invoice.pdf
"""
import json, sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

from reportlab.lib.fonts import addMapping
FONT = "Helvetica"
for reg, bold in (("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
                  ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
                  ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf")):
    try:
        pdfmetrics.registerFont(TTFont("Main", reg)); pdfmetrics.registerFont(TTFont("Main-Bold", bold))
        addMapping("Main", 0, 0, "Main"); addMapping("Main", 1, 0, "Main-Bold")
        FONT = "Main"; break
    except Exception:
        continue


def money(n, cur):
    return f"{n:,.0f}".replace(",", " ") + f" {cur}"


def build(data, out):
    cur = data.get("currency", "so'm")
    st = ParagraphStyle("n", fontName=FONT, fontSize=10, leading=14)
    big = ParagraphStyle("b", fontName=FONT, fontSize=20, leading=24, textColor=colors.HexColor("#1F4E78"))
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm)
    s = data["seller"]; b = data["buyer"]
    els = [Paragraph(f"HISOB-FAKTURA № {data['number']}", big), Paragraph(f"Sana: {data['date']}", st), Spacer(1, 8 * mm)]
    parties = Table([[Paragraph(f"<b>Sotuvchi</b><br/>{s['name']}<br/>{s.get('address','')}<br/>{s.get('phone','')}<br/>STIR: {s.get('tin','')}", st),
                      Paragraph(f"<b>Xaridor</b><br/>{b['name']}<br/>{b.get('address','')}<br/>{b.get('phone','')}", st)]], colWidths=[87 * mm, 87 * mm])
    els += [parties, Spacer(1, 8 * mm)]
    rows = [["#", "Nomi", "Soni", "Narxi", "Summa"]]
    total = 0
    for i, it in enumerate(data["items"], 1):
        sm = it["qty"] * it["price"]; total += sm
        rows.append([i, Paragraph(it["name"], st), it["qty"], money(it["price"], cur), money(sm, cur)])
    vat = total * data.get("vat_percent", 0) / 100
    rows += [["", "", "", "Jami:", money(total, cur)]]
    if vat:
        rows += [["", "", "", f"QQS {data['vat_percent']}%:", money(vat, cur)], ["", "", "", "To'lovga:", money(total + vat, cur)]]
    t = Table(rows, colWidths=[10 * mm, 76 * mm, 18 * mm, 34 * mm, 36 * mm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), FONT, 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, len(data["items"])), 0.5, colors.HexColor("#BBBBBB")),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, len(data["items"])), [colors.white, colors.HexColor("#F2F6FA")]),
    ]))
    els += [t, Spacer(1, 10 * mm), Paragraph(data.get("note", ""), st), Spacer(1, 14 * mm),
            Paragraph("Imzo: ____________________          M.O'.", st)]
    doc.build(els)
    return total + vat


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "invoice.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "invoice.pdf"
    print("Tayyor:", out, "| to'lovga:", build(json.load(open(src, encoding="utf-8")), out))
''')
w("hisob-faktura-pdf/invoice.json", '''
{
  "number": "2026-041",
  "date": "04.11.2026",
  "currency": "so'm",
  "vat_percent": 12,
  "seller": {"name": "\\"Sizning kompaniya\\" MChJ", "address": "Toshkent sh., Yunusobod t., 12-uy", "phone": "+998 90 000 00 00", "tin": "300000000"},
  "buyer": {"name": "Mijoz MChJ", "address": "Samarqand sh., Registon ko'chasi 1", "phone": "+998 91 111 11 11"},
  "items": [
    {"name": "Veb-sayt yaratish (landing page)", "qty": 1, "price": 3500000},
    {"name": "Telegram bot sozlash", "qty": 1, "price": 1500000},
    {"name": "Oylik texnik qo'llab-quvvatlash", "qty": 3, "price": 400000}
  ],
  "note": "To'lov 5 bank kuni ichida amalga oshirilishi so'raladi. Rahmat!"
}
''')
w("hisob-faktura-pdf/README.md", '''
# Hisob-faktura (invoice) PDF generatori

`invoice.json` faylidagi ma'lumotdan chiroyli, jadvalli PDF hisob-faktura yasaydi: raqam, sana, sotuvchi/xaridor, mahsulotlar, jami, QQS, imzo joyi.

## O'rnatish
```
pip install reportlab
```

## Ishlatish
1. `invoice.json` ni o'z ma'lumotlaringiz bilan to'ldiring (Bloknot yoki VS Code'da).
2. `python invoice.py invoice.json hisob.pdf`

💡 QQS kerak bo'lmasa `"vat_percent": 0` qiling. Valyutani `"currency": "USD"` qilib o'zgartirsa bo'ladi.
⚠️ Bu oddiy tijorat hujjati namunasi. Rasmiy elektron hisob-faktura (soliq tizimi orqali) uchun soliq.uz/didox kabi tizimlardan foydalaning.
''')
print("ok code1")
