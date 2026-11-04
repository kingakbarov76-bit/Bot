# Kod loyihalari 6-10
import os, textwrap
B = "/home/claude/bot/paid/src"
def w(path, s):
    p = os.path.join(B, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(textwrap.dedent(s).lstrip("\n"))

# ---------------------------------------------------------------- C6: sayt formasi -> Telegram (Cloudflare Worker orqali, token yashirin)
w("forma-telegramga/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ariza qoldiring</title>
<style>
  :root { --c:#2563eb; }
  * { box-sizing:border-box; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  body { margin:0; min-height:100vh; display:grid; place-items:center; background:linear-gradient(135deg,#eef2ff,#f8fafc); padding:16px; }
  form { width:100%; max-width:420px; background:#fff; padding:28px; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,.08); }
  h1 { margin:0 0 6px; font-size:24px; } p { margin:0 0 18px; color:#64748b; }
  label { display:block; font-size:14px; margin:12px 0 6px; color:#334155; }
  input, textarea, select { width:100%; padding:12px; border:1px solid #cbd5e1; border-radius:10px; font-size:16px; }
  textarea { min-height:90px; resize:vertical; }
  button { width:100%; margin-top:18px; padding:14px; border:0; border-radius:10px; background:var(--c); color:#fff; font-size:16px; font-weight:600; cursor:pointer; }
  button:disabled { opacity:.6; }
  .msg { margin-top:14px; font-size:15px; text-align:center; } .ok { color:#16a34a; } .err { color:#dc2626; }
  .hp { position:absolute; left:-9999px; }
</style>
</head>
<body>
<form id="f" novalidate>
  <h1>Ariza qoldiring</h1>
  <p>15 daqiqa ichida bog'lanamiz.</p>
  <label for="name">Ismingiz</label><input id="name" name="name" required maxlength="60">
  <label for="phone">Telefon</label><input id="phone" name="phone" required placeholder="+998 90 123 45 67" inputmode="tel">
  <label for="service">Xizmat</label>
  <select id="service" name="service"><option>Konsultatsiya</option><option>Sayt yaratish</option><option>Telegram bot</option><option>Boshqa</option></select>
  <label for="text">Izoh</label><textarea id="text" name="text" maxlength="800"></textarea>
  <input class="hp" name="website" tabindex="-1" autocomplete="off">
  <button id="btn" type="submit">Yuborish</button>
  <div id="msg" class="msg" role="status"></div>
</form>
<script>
// 1) worker.js ni Cloudflare'ga joylang, 2) shu yerga o'sha manzilni yozing:
const ENDPOINT = "https://YOUR-WORKER.YOUR-NAME.workers.dev";
const f = document.getElementById("f"), msg = document.getElementById("msg"), btn = document.getElementById("btn");
function validPhone(v) { return v.replace(/\\D/g, "").length >= 9; }
f.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(f));
  if (!data.name.trim() || !validPhone(data.phone)) { msg.className = "msg err"; msg.textContent = "Ism va telefonni to'g'ri kiriting."; return; }
  if (data.website) return; // spam bot
  btn.disabled = true; msg.className = "msg"; msg.textContent = "Yuborilmoqda...";
  try {
    const r = await fetch(ENDPOINT, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(data) });
    if (!r.ok) throw new Error(r.status);
    msg.className = "msg ok"; msg.textContent = "✅ Rahmat! Arizangiz qabul qilindi."; f.reset();
  } catch (err) {
    msg.className = "msg err"; msg.textContent = "Xatolik. Birozdan keyin qayta urinib ko'ring.";
  } finally { btn.disabled = false; }
});
</script>
</body>
</html>
''')
w("forma-telegramga/worker.js", '''
// Cloudflare Worker: receives the form and forwards it to your Telegram. Bot token stays secret (not in the website code).
// Settings -> Variables: BOT_TOKEN (secret), CHAT_ID (your id), ALLOWED_ORIGIN (e.g. https://mysite.uz or *)
export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type",
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405, headers: cors });
    let d;
    try { d = await request.json(); } catch { return new Response("Bad JSON", { status: 400, headers: cors }); }
    const clean = (s, n) => String(s || "").replace(/[<>&]/g, "").slice(0, n);
    if (d.website) return new Response("ok", { headers: cors }); // honeypot
    const text = `📩 Yangi ariza\\n👤 ${clean(d.name, 60)}\\n📞 ${clean(d.phone, 30)}\\n🛠 ${clean(d.service, 40)}\\n💬 ${clean(d.text, 800)}`;
    const r = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ chat_id: env.CHAT_ID, text }),
    });
    return new Response(r.ok ? "ok" : "telegram error", { status: r.ok ? 200 : 502, headers: cors });
  },
};
''')
w("forma-telegramga/README.md", '''
# Saytdagi ariza formasi → to'g'ridan-to'g'ri Telegramingizga

Mijoz saytda ism, telefon, izoh yozadi → sizga Telegram'da xabar keladi. Bot token sayt kodida ko'rinmaydi (xavfsiz), chunki xabar Cloudflare Worker orqali o'tadi. Cloudflare Worker bepul (kuniga 100 000 so'rovgacha).

## Sozlash (15 daqiqa)
1. @BotFather'da bot yarating, token oling. Botga /start yozing. @userinfobot'dan o'z ID'ingizni oling.
2. dash.cloudflare.com → ro'yxatdan o'ting → Workers & Pages → Create → Worker → "Hello World" → Deploy → Edit code.
3. `worker.js` ichidagi kodni to'liq qo'ying → Deploy.
4. Worker → Settings → Variables and Secrets: `BOT_TOKEN` (Secret), `CHAT_ID` (ID raqamingiz), `ALLOWED_ORIGIN` (saytingiz manzili yoki `*`).
5. `index.html` dagi `ENDPOINT` ga worker manzilini yozing (masalan `https://forma.ismingiz.workers.dev`).
6. `index.html` ni saytingizga qo'ying (yoki shu forma kodini mavjud sahifangizga ko'chiring).

## Nimalar bor
- Telefon raqamini tekshirish, spam botlardan himoya (yashirin maydon)
- Mobilga moslashgan dizayn
- Xabar: ism, telefon, xizmat turi, izoh
''')

# ---------------------------------------------------------------- C7: xarajatlar hisobchisi (bitta HTML, internet kerak emas)
w("xarajat-hisobchi/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Xarajatlar hisobchisi</title>
<style>
  * { box-sizing:border-box; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  body { margin:0; background:#0f172a; color:#e2e8f0; }
  .wrap { max-width:720px; margin:0 auto; padding:20px 16px 60px; }
  h1 { font-size:22px; margin:6px 0 16px; }
  .card { background:#1e293b; border-radius:14px; padding:16px; margin-bottom:14px; }
  .row { display:flex; gap:8px; flex-wrap:wrap; }
  input, select, button { padding:11px; border-radius:10px; border:1px solid #334155; background:#0f172a; color:#e2e8f0; font-size:15px; }
  input[type=number] { width:130px; } input[type=text] { flex:1; min-width:140px; }
  button { background:#22c55e; color:#052e16; font-weight:700; border:0; cursor:pointer; }
  .sum { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
  .sum div { background:#0f172a; border-radius:10px; padding:10px; } .sum b { display:block; font-size:18px; margin-top:4px; }
  table { width:100%; border-collapse:collapse; font-size:14px; } td, th { padding:8px 6px; border-bottom:1px solid #334155; text-align:left; }
  td:last-child { text-align:right; } .del { background:none; color:#f87171; padding:2px 6px; }
  .bar { height:10px; background:#22c55e; border-radius:6px; } .cat { display:grid; grid-template-columns:110px 1fr 110px; gap:8px; align-items:center; margin:6px 0; font-size:14px; }
  .muted { color:#94a3b8; font-size:13px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>💰 Xarajatlar hisobchisi</h1>
  <div class="card">
    <div class="row">
      <input id="amount" type="number" min="0" placeholder="Summa">
      <select id="cat"><option>Oziq-ovqat</option><option>Transport</option><option>Uy-joy</option><option>Kommunal</option><option>Aloqa</option><option>Kiyim</option><option>Sog'liq</option><option>Ta'lim</option><option>Ko'ngilochar</option><option>Boshqa</option></select>
      <input id="note" type="text" placeholder="Izoh (ixtiyoriy)">
      <input id="date" type="date">
      <button id="add">Qo'shish</button>
    </div>
    <p class="muted">Ma'lumotlar faqat shu brauzerda saqlanadi. Internet kerak emas.</p>
  </div>
  <div class="card">
    <div class="row" style="justify-content:space-between;align-items:center">
      <input id="month" type="month">
      <div class="row"><button id="csv" style="background:#38bdf8;color:#082f49">CSV yuklab olish</button></div>
    </div>
    <div class="sum" style="margin-top:12px">
      <div>Shu oy<b id="tMonth">0</b></div><div>Kunlik o'rtacha<b id="tAvg">0</b></div><div>Yozuvlar<b id="tCount">0</b></div>
    </div>
  </div>
  <div class="card"><b>Toifalar bo'yicha</b><div id="cats"></div></div>
  <div class="card"><table><thead><tr><th>Sana</th><th>Toifa</th><th>Izoh</th><th>Summa</th></tr></thead><tbody id="list"></tbody></table></div>
</div>
<script>
const KEY = "xarajatlar_v1";
const $ = (id) => document.getElementById(id);
let items = [];
try { items = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch { items = []; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(items)); } catch {} };
const fmt = (n) => Math.round(n).toLocaleString("ru-RU").replace(/\\u00a0/g, " ") + " so'm";
const today = new Date().toISOString().slice(0, 10);
$("date").value = today; $("month").value = today.slice(0, 7);

function render() {
  const m = $("month").value;
  const list = items.filter((x) => x.date.startsWith(m)).sort((a, b) => b.date.localeCompare(a.date));
  const total = list.reduce((s, x) => s + x.amount, 0);
  const [y, mm] = m.split("-").map(Number);
  const days = m === today.slice(0, 7) ? Number(today.slice(8)) : new Date(y, mm, 0).getDate();
  $("tMonth").textContent = fmt(total); $("tAvg").textContent = fmt(total / days); $("tCount").textContent = list.length;
  const byCat = {};
  list.forEach((x) => (byCat[x.cat] = (byCat[x.cat] || 0) + x.amount));
  const max = Math.max(1, ...Object.values(byCat));
  $("cats").innerHTML = Object.entries(byCat).sort((a, b) => b[1] - a[1]).map(([c, v]) =>
    `<div class="cat"><span>${c}</span><div class="bar" style="width:${(v / max) * 100}%"></div><span>${fmt(v)}</span></div>`).join("") || '<p class="muted">Bu oyda yozuv yo\\'q.</p>';
  $("list").innerHTML = list.map((x) =>
    `<tr><td>${x.date.slice(5)}</td><td>${x.cat}</td><td>${x.note.replace(/[<>&]/g, "")}</td><td>${fmt(x.amount)} <button class="del" data-id="${x.id}">✕</button></td></tr>`).join("");
}
$("add").onclick = () => {
  const amount = Number($("amount").value);
  if (!(amount > 0)) { $("amount").focus(); return; }
  items.push({ id: Date.now() + Math.random(), amount, cat: $("cat").value, note: $("note").value.trim(), date: $("date").value || today });
  save(); $("amount").value = ""; $("note").value = ""; render();
};
$("list").onclick = (e) => { const id = e.target.dataset.id; if (id) { items = items.filter((x) => String(x.id) !== id); save(); render(); } };
$("month").onchange = render;
$("csv").onclick = () => {
  const rows = [["date", "category", "note", "amount"], ...items.map((x) => [x.date, x.cat, x.note, x.amount])];
  const csv = rows.map((r) => r.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob(["\\ufeff" + csv], { type: "text/csv" })); a.download = "xarajatlar.csv"; a.click();
};
render();
</script>
</body>
</html>
''')
w("xarajat-hisobchi/README.md", '''
# Shaxsiy xarajatlar hisobchisi (bitta HTML fayl)

Telefon yoki kompyuterda ishlaydi, internet va ro'yxatdan o'tish kerak emas. Pul qayerga ketayotganini ko'rsatadi.

## Imkoniyatlar
- Summa, toifa, izoh, sana bilan xarajat qo'shish
- Oy bo'yicha jami, kunlik o'rtacha, toifalar diagrammasi
- Excel uchun CSV yuklab olish
- Ma'lumotlar brauzerda saqlanadi (boshqa joyga yuborilmaydi)

## Ishlatish
- Kompyuter: `index.html` ni ikki marta bosing.
- Telefon: faylni telefonga o'tkazing va brauzerda (Chrome) oching. Yoki GitHub Pages / Netlify'ga bepul joylab, «Bosh ekranga qo'shish» qiling, ilova kabi ishlaydi.

💡 Toifalarni o'zgartirish: `index.html` ichidagi `<option>` qatorlarini tahrirlang.
''')

# ---------------------------------------------------------------- C8: fayllarni saralash
w("fayl-saralash/organize.py", '''
"""Sort a messy folder (e.g. Downloads) into subfolders by file type. Safe: dry-run first, undo log.
Usage:
  python organize.py "C:/Users/Me/Downloads" --dry-run   # show what would happen
  python organize.py "C:/Users/Me/Downloads"             # do it
  python organize.py "C:/Users/Me/Downloads" --undo      # put everything back
"""
import argparse, json, pathlib, shutil

TYPES = {
    "Rasmlar": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".svg"},
    "Videolar": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Musiqa": {".mp3", ".wav", ".m4a", ".ogg", ".flac"},
    "Hujjatlar": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".ppt", ".pptx"},
    "Jadvallar": {".xls", ".xlsx", ".csv", ".ods"},
    "Arxivlar": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Dasturlar": {".exe", ".msi", ".apk", ".dmg", ".deb"},
    "Kod": {".py", ".js", ".html", ".css", ".json", ".php", ".java", ".sql"},
}
LOG = ".organize_log.json"


def category(p):
    ext = p.suffix.lower()
    return next((name for name, exts in TYPES.items() if ext in exts), "Boshqa")


def unique(dst):
    if not dst.exists():
        return dst
    i = 1
    while True:
        cand = dst.with_name(f"{dst.stem} ({i}){dst.suffix}")
        if not cand.exists():
            return cand
        i += 1


def organize(folder, dry):
    moves = []
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.name != LOG and not p.name.startswith("."):
            dst = unique(folder / category(p) / p.name)
            moves.append((str(p), str(dst)))
            print(("[sinov] " if dry else "") + f"{p.name}  →  {dst.parent.name}/")
            if not dry:
                dst.parent.mkdir(exist_ok=True)
                shutil.move(str(p), str(dst))
    if not dry and moves:
        (folder / LOG).write_text(json.dumps(moves, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Jami: {len(moves)} ta fayl" + (" (hech narsa ko'chirilmadi, bu sinov)" if dry else ""))
    return moves


def undo(folder):
    log = folder / LOG
    if not log.exists():
        print("Qaytarish uchun yozuv topilmadi."); return 0
    moves = json.loads(log.read_text(encoding="utf-8"))
    for src, dst in reversed(moves):
        if pathlib.Path(dst).exists():
            shutil.move(dst, unique(pathlib.Path(src)))
    for d in TYPES.keys() | {"Boshqa"}:
        sub = folder / d
        if sub.is_dir() and not any(sub.iterdir()):
            sub.rmdir()
    log.unlink(); print(f"Qaytarildi: {len(moves)} ta fayl")
    return len(moves)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--undo", action="store_true")
    a = ap.parse_args()
    f = pathlib.Path(a.folder).expanduser()
    undo(f) if a.undo else organize(f, a.dry_run)
''')
w("fayl-saralash/README.md", '''
# «Yuklab olinganlar» papkasini avtomatik tartiblash

Yuzlab aralash faylni turiga qarab papkalarga ajratadi: Rasmlar, Videolar, Hujjatlar, Jadvallar, Arxivlar, Dasturlar, Kod, Musiqa, Boshqa.

**Xavfsiz:**
- `--dry-run` avval nima bo'lishini ko'rsatadi, hech narsani ko'chirmaydi;
- bir xil nomli fayl ustidan yozmaydi (`fayl (1).pdf` qiladi);
- `--undo` hammasini joyiga qaytaradi.

## Ishlatish (Python 3.8+, qo'shimcha kutubxona kerak emas)
```
python organize.py "C:/Users/Ism/Downloads" --dry-run
python organize.py "C:/Users/Ism/Downloads"
python organize.py "C:/Users/Ism/Downloads" --undo
```
💡 Toifalarni `TYPES` ro'yxatida o'zgartirasiz.
''')

# ---------------------------------------------------------------- C9: valyuta kursi (Markaziy bank)
w("valyuta-kursi/rates.py", '''
"""Official exchange rates from the Central Bank of Uzbekistan (cbu.uz) + converter + history CSV.
Usage:
  python rates.py                 # today's main rates
  python rates.py 100 USD         # convert 100 USD to UZS
  python rates.py 1500000 UZS EUR # convert UZS to EUR
  python rates.py --save          # append today's rates to rates_history.csv
"""
import csv, datetime, json, pathlib, sys, urllib.request

URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
MAIN = ["USD", "EUR", "RUB", "KZT", "CNY", "GBP", "TRY"]


def fetch(url=URL):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 rates-script"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return parse(json.loads(r.read().decode("utf-8")))


def parse(data):
    """Return {code: (rate_in_uzs_per_1_unit, diff, date)} from cbu.uz JSON."""
    out = {}
    for x in data:
        nominal = float(x.get("Nominal", 1) or 1)
        out[x["Ccy"]] = (float(x["Rate"]) / nominal, float(x.get("Diff", 0) or 0), x.get("Date", ""))
    return out


def convert(rates, amount, src, dst="UZS"):
    src, dst = src.upper(), dst.upper()
    uzs = amount if src == "UZS" else amount * rates[src][0]
    return uzs if dst == "UZS" else uzs / rates[dst][0]


def main(argv):
    rates = fetch()
    if "--save" in argv:
        f = pathlib.Path("rates_history.csv"); new = not f.exists()
        with f.open("a", newline="", encoding="utf-8") as fh:
            wr = csv.writer(fh)
            if new:
                wr.writerow(["date"] + MAIN)
            wr.writerow([datetime.date.today().isoformat()] + [rates[c][0] for c in MAIN if c in rates])
        print("Saqlandi:", f); return
    if len(argv) >= 2:
        amount, src = float(argv[0].replace(" ", "")), argv[1]
        dst = argv[2] if len(argv) > 2 else "UZS"
        res = convert(rates, amount, src, dst)
        print(f"{amount:,.2f} {src.upper()} = {res:,.2f} {dst.upper()}".replace(",", " ")); return
    date = next(iter(rates.values()))[2]
    print(f"Markaziy bank kursi ({date}):")
    for c in MAIN:
        if c in rates:
            r, d, _ = rates[c]
            print(f"  1 {c} = {r:,.2f} so'm ({'+' if d >= 0 else ''}{d})".replace(",", " "))


if __name__ == "__main__":
    main(sys.argv[1:])
''')
w("valyuta-kursi/test_rates.py", '''
"""Offline test with a saved sample of the cbu.uz response format."""
import json, rates
sample = json.load(open("sample.json", encoding="utf-8"))
r = rates.parse(sample)
assert "USD" in r and r["USD"][0] > 1000
usd = r["USD"][0]
assert abs(rates.convert(r, 100, "USD") - 100 * usd) < 1e-6
assert abs(rates.convert(r, 100 * usd, "UZS", "USD") - 100) < 1e-6
print("TEST OK: 1 USD =", usd)
''')
w("valyuta-kursi/README.md", '''
# Markaziy bank valyuta kursi + konvertor (Python)

O'zbekiston Markaziy banki (cbu.uz) rasmiy kurslarini oladi, summani istalgan valyutaga o'giradi va kurslar tarixini CSV faylga yig'adi.

## Ishlatish (Python 3.8+, qo'shimcha kutubxona kerak emas)
```
python rates.py                  # bugungi asosiy kurslar
python rates.py 100 USD          # 100 dollar necha so'm
python rates.py 1500000 UZS EUR  # 1,5 mln so'm necha yevro
python rates.py --save           # bugungi kursni rates_history.csv ga qo'shish
```
💡 Har kuni avtomatik saqlash: Windows «Task Scheduler» yoki Linux `cron` orqali `--save` ni kuniga bir marta ishga tushiring, keyin CSV'ni Excel'da grafikka aylantiring.

`python test_rates.py` internetsiz test (namuna fayl bilan).
''')

# ---------------------------------------------------------------- C10: test (quiz) yaratuvchi
w("test-yaratuvchi/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test yaratuvchi</title>
<style>
  * { box-sizing:border-box; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  body { margin:0; background:#f1f5f9; color:#0f172a; } .wrap { max-width:760px; margin:0 auto; padding:20px 16px 60px; }
  .card { background:#fff; border-radius:14px; padding:18px; margin:12px 0; box-shadow:0 2px 10px rgba(0,0,0,.05); }
  textarea { width:100%; min-height:220px; padding:12px; border-radius:10px; border:1px solid #cbd5e1; font:14px/1.5 ui-monospace, Menlo, monospace; }
  button { padding:12px 16px; border:0; border-radius:10px; background:#4f46e5; color:#fff; font-weight:600; cursor:pointer; font-size:15px; }
  .opt { display:block; padding:12px; margin:8px 0; border:2px solid #e2e8f0; border-radius:10px; cursor:pointer; background:#fff; width:100%; text-align:left; font-size:15px; color:#0f172a; }
  .opt.right { border-color:#22c55e; background:#f0fdf4; } .opt.wrong { border-color:#ef4444; background:#fef2f2; }
  .top { display:flex; justify-content:space-between; color:#475569; font-size:14px; } .hidden { display:none; }
  .big { font-size:40px; font-weight:800; margin:8px 0; } .muted { color:#64748b; font-size:13px; }
</style>
</head>
<body>
<div class="wrap">
  <div id="editor" class="card">
    <h2 style="margin-top:0">📝 Test yaratuvchi</h2>
    <p class="muted">Har savolni quyidagi formatda yozing. To'g'ri javob oldiga <b>*</b> qo'ying. Savollar orasida bo'sh qator.</p>
    <textarea id="src">O'zbekiston poytaxti qaysi shahar?
*Toshkent
Samarqand
Buxoro
Xiva

5 x 6 = ?
25
*30
36

Qaysi biri dasturlash tili?
*Python
Photoshop
Excel</textarea>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center">
      <label>Vaqt (daqiqa): <input id="mins" type="number" value="5" min="0" style="width:70px;padding:8px"></label>
      <label><input id="shuffle" type="checkbox" checked> Aralashtirish</label>
      <button id="start">▶ Testni boshlash</button>
    </div>
    <p id="err" class="muted" style="color:#dc2626"></p>
  </div>
  <div id="quiz" class="card hidden">
    <div class="top"><span id="prog"></span><span id="timer"></span></div>
    <h3 id="q"></h3><div id="opts"></div>
  </div>
  <div id="result" class="card hidden" style="text-align:center">
    <div>Natija</div><div class="big" id="score"></div><div id="pct" class="muted"></div>
    <div id="review" style="text-align:left;margin-top:14px"></div>
    <button onclick="location.reload()" style="margin-top:12px">Qaytadan</button>
  </div>
</div>
<script>
const $ = (id) => document.getElementById(id);
function parse(text) {
  return text.trim().split(/\\n\\s*\\n/).map((block) => {
    const lines = block.split("\\n").map((l) => l.trim()).filter(Boolean);
    const q = lines.shift();
    const opts = lines.map((l) => ({ t: l.replace(/^\\*/, "").trim(), ok: l.startsWith("*") }));
    return { q, opts };
  }).filter((x) => x.q && x.opts.length >= 2 && x.opts.filter((o) => o.ok).length === 1);
}
const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
let qs = [], i = 0, score = 0, answers = [], timerId = null;
$("start").onclick = () => {
  qs = parse($("src").value);
  if (!qs.length) { $("err").textContent = "Savol topilmadi. Har savolda bitta * li to'g'ri javob bo'lsin."; return; }
  if ($("shuffle").checked) { shuffle(qs); qs.forEach((x) => shuffle(x.opts)); }
  $("editor").classList.add("hidden"); $("quiz").classList.remove("hidden");
  const mins = Number($("mins").value);
  if (mins > 0) {
    let left = mins * 60;
    const tick = () => { $("timer").textContent = `⏱ ${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}`; if (left-- <= 0) finish(); };
    tick(); timerId = setInterval(tick, 1000);
  }
  show();
};
function show() {
  const x = qs[i];
  $("prog").textContent = `Savol ${i + 1} / ${qs.length}`; $("q").textContent = x.q; $("opts").innerHTML = "";
  x.opts.forEach((o, k) => {
    const b = document.createElement("button"); b.className = "opt"; b.textContent = o.t;
    b.onclick = () => {
      [...$("opts").children].forEach((c, n) => { c.disabled = true; if (x.opts[n].ok) c.classList.add("right"); });
      if (!o.ok) b.classList.add("wrong"); else score++;
      answers.push({ q: x.q, your: o.t, right: x.opts.find((z) => z.ok).t, ok: o.ok });
      setTimeout(() => { i++; i < qs.length ? show() : finish(); }, 700);
    };
    $("opts").appendChild(b);
  });
}
function finish() {
  clearInterval(timerId); $("quiz").classList.add("hidden"); $("result").classList.remove("hidden");
  $("score").textContent = `${score} / ${qs.length}`; $("pct").textContent = `${Math.round((score / qs.length) * 100)}%`;
  $("review").innerHTML = answers.filter((a) => !a.ok).map((a) => `<p>❌ <b>${a.q.replace(/[<>&]/g, "")}</b><br>Sizniki: ${a.your.replace(/[<>&]/g, "")} · To'g'ri: ${a.right.replace(/[<>&]/g, "")}</p>`).join("");
}
</script>
</body>
</html>
''')
w("test-yaratuvchi/README.md", '''
# Test (quiz) yaratuvchi: o'qituvchi va o'quv markazlari uchun

Savollarni oddiy matn qilib yozasiz → bir tugma bilan vaqtli, aralashtirilgan test tayyor. Oxirida ball, foiz va xato javoblar tahlili chiqadi.

## Format
```
Savol matni?
*To'g'ri javob
Noto'g'ri javob
Noto'g'ri javob

Keyingi savol?
...
```
To'g'ri javob oldiga `*`, savollar orasida bo'sh qator.

## Ishlatish
- `index.html` ni brauzerda oching, savollarni yozing, «Testni boshlash».
- O'quvchilarga berish: savollarni `index.html` ichidagi `<textarea>` ga yozib saqlang, faylni Telegram guruhga tashlang yoki GitHub Pages / Netlify'ga bepul joylang.

💡 ChatGPT'dan «shu mavzuda 20 ta test savoli, to'g'ri javob oldida * bilan» deb so'rasangiz, formatga mos savollar oladi.
''')
print("ok code2")
