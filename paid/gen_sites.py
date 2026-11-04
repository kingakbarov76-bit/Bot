# 5 ta tayyor sayt (HTML/CSS/JS, internet va kutubxonasiz ishlaydi)
import os, textwrap
B = "/home/claude/bot/paid/src"
def w(path, s):
    p = os.path.join(B, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(textwrap.dedent(s).lstrip("\n"))

BASE_CSS = '''
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
.container{width:min(1120px,100% - 32px);margin-inline:auto}
.nav{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.nav .container{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}
.logo{font-weight:800;font-size:20px;letter-spacing:-.02em}
.menu{display:flex;gap:22px;font-size:15px}
.menu a:hover{color:var(--accent)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:13px 22px;border-radius:12px;background:var(--accent);color:var(--on-accent);font-weight:700;border:0;cursor:pointer;font-size:15px}
.btn.ghost{background:transparent;color:var(--ink);border:1.5px solid var(--line)}
section{padding:72px 0}
h1{font-size:clamp(34px,6vw,60px);line-height:1.05;letter-spacing:-.03em}
h2{font-size:clamp(26px,4vw,38px);letter-spacing:-.02em;margin-bottom:10px}
.lead{font-size:18px;color:var(--muted);max-width:560px;margin:16px 0 26px}
.muted{color:var(--muted)}
.grid{display:grid;gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px}
footer{padding:30px 0;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
.burger{display:none;background:none;border:0;font-size:26px;color:var(--ink)}
@media(max-width:760px){.menu{display:none;position:absolute;top:64px;left:0;right:0;flex-direction:column;background:var(--bg);padding:16px;border-bottom:1px solid var(--line)}.menu.open{display:flex}.burger{display:block}section{padding:52px 0}}
.nav .container>div:last-child{display:flex;gap:8px;align-items:center;flex-shrink:0}
@media(max-width:760px){.nav .btn:not(.cartbtn){padding:9px 12px;font-size:13px}.logo{font-size:18px}}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111;color:#fff;padding:12px 18px;border-radius:12px;opacity:0;transition:.3s;pointer-events:none;z-index:99}
.toast.show{opacity:1}
'''

CART_JS = '''
// ====== SOZLAMALAR: o'zingiznikiga almashtiring ======
const PHONE = "998901234567";      // WhatsApp raqam (faqat raqamlar)
const TG_USERNAME = "username";    // Telegram username (@ belgisisiz)
// ====================================================
const cart = {};
const fmt = (n) => n.toLocaleString("ru-RU").replace(/\\u00a0/g, " ") + " so'm";
function toast(t) { const el = document.getElementById("toast"); el.textContent = t; el.classList.add("show"); setTimeout(() => el.classList.remove("show"), 1600); }
function addToCart(id, name, price) { cart[id] = cart[id] || { name, price, qty: 0 }; cart[id].qty++; renderCart(); toast("✅ " + name + " qo'shildi"); }
function changeQty(id, d) { if (!cart[id]) return; cart[id].qty += d; if (cart[id].qty <= 0) delete cart[id]; renderCart(); }
function cartTotal() { return Object.values(cart).reduce((s, x) => s + x.price * x.qty, 0); }
function renderCart() {
  const items = Object.entries(cart);
  document.getElementById("cartCount").textContent = items.reduce((s, [, x]) => s + x.qty, 0);
  document.getElementById("cartItems").innerHTML = items.length ? items.map(([id, x]) =>
    `<div class="ci"><div><b>${x.name}</b><div class="muted">${fmt(x.price)}</div></div>
     <div class="qty"><button onclick="changeQty('${id}',-1)">−</button><span>${x.qty}</span><button onclick="changeQty('${id}',1)">+</button></div></div>`).join("")
    : '<p class="muted">Savat bo\\'sh</p>';
  document.getElementById("cartTotal").textContent = fmt(cartTotal());
}
function orderText() {
  const name = document.getElementById("cName").value.trim(), phone = document.getElementById("cPhone").value.trim(), addr = document.getElementById("cAddr").value.trim();
  if (!Object.keys(cart).length) { toast("Savat bo'sh"); return null; }
  if (!name || phone.replace(/\\D/g, "").length < 9) { toast("Ism va telefonni kiriting"); return null; }
  const lines = Object.values(cart).map((x) => `• ${x.name} × ${x.qty} = ${fmt(x.price * x.qty)}`);
  return `🛒 Buyurtma\\n${lines.join("\\n")}\\nJami: ${fmt(cartTotal())}\\n\\n👤 ${name}\\n📞 ${phone}\\n📍 ${addr || "-"}`;
}
function sendWhatsApp() { const t = orderText(); if (t) window.open(`https://wa.me/${PHONE}?text=${encodeURIComponent(t)}`, "_blank"); }
async function sendTelegram() {
  const t = orderText(); if (!t) return;
  try { await navigator.clipboard.writeText(t); toast("Buyurtma nusxalandi: Telegram'da yuboring"); } catch { prompt("Nusxa oling va Telegram'da yuboring:", t); }
  setTimeout(() => window.open(`https://t.me/${TG_USERNAME}`, "_blank"), 600);
}
function toggleCart(open) { document.getElementById("drawer").classList.toggle("open", open); }
document.querySelector(".burger")?.addEventListener("click", () => document.querySelector(".menu").classList.toggle("open"));
renderCart();
'''

CART_CSS = '''
.cartbtn{position:relative}
.cartbtn span{position:absolute;top:-6px;right:-6px;background:#ef4444;color:#fff;border-radius:99px;font-size:12px;min-width:20px;height:20px;display:grid;place-items:center}
.drawer{position:fixed;inset:0 0 0 auto;width:min(420px,100%);background:var(--card);border-left:1px solid var(--line);transform:translateX(100%);transition:.3s;z-index:50;display:flex;flex-direction:column;padding:20px;gap:12px;box-shadow:-10px 0 30px rgba(0,0,0,.15)}
.drawer.open{transform:none}
.drawer input{width:100%;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);font-size:15px}
.ci{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)}
.qty{display:flex;align-items:center;gap:10px}.qty button{width:30px;height:30px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink);cursor:pointer;font-size:16px}
#cartItems{flex:1;overflow:auto}
'''

# ============================================================== S1 KAFE
w("sayt-kafe/style.css", ":root{--bg:#fffaf3;--card:#fff;--ink:#2b1d12;--muted:#7a6a5c;--line:#efe3d3;--accent:#d9480f;--on-accent:#fff}\n" + BASE_CSS + CART_CSS + '''
.hero{padding:70px 0 40px;background:radial-gradient(900px 400px at 85% 10%,#ffe8cc,transparent)}
.hero .container{display:grid;grid-template-columns:1.1fr .9fr;gap:30px;align-items:center}
.plate{aspect-ratio:1;border-radius:50%;background:conic-gradient(from 30deg,#ffd8a8,#ffa94d,#e8590c,#ffd8a8);display:grid;place-items:center;font-size:120px;box-shadow:0 30px 60px rgba(217,72,15,.25)}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}
.tabs button{padding:9px 16px;border-radius:99px;border:1px solid var(--line);background:#fff;cursor:pointer;font-size:14px}
.tabs button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.menu-grid{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.dish{display:flex;flex-direction:column;gap:8px}
.dish .em{font-size:44px;background:#fff4e6;border-radius:14px;height:110px;display:grid;place-items:center}
.dish .row{display:flex;justify-content:space-between;align-items:center;margin-top:auto}
.dish button{padding:9px 14px;border-radius:10px;border:0;background:var(--accent);color:#fff;font-weight:700;cursor:pointer}
.info{grid-template-columns:repeat(3,1fr)}
@media(max-width:760px){.hero .container{grid-template-columns:1fr}.plate{width:min(260px,70vw);margin:auto;font-size:90px}.info{grid-template-columns:1fr}}
''')
w("sayt-kafe/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lazzat kafe: mazali taomlar, tez yetkazib berish</title>
<meta name="description" content="Milliy va fast-food taomlar. Onlayn buyurtma, 40 daqiqada yetkazib berish.">
<link rel="stylesheet" href="style.css"></head>
<body>
<nav class="nav"><div class="container">
  <a class="logo" href="#">🍽 Lazzat</a>
  <div class="menu"><a href="#menyu">Menyu</a><a href="#info">Manzil</a><a href="#aloqa">Aloqa</a></div>
  <div style="display:flex;gap:8px;align-items:center"><button class="btn cartbtn" onclick="toggleCart(true)">🛒<span id="cartCount">0</span></button><button class="burger" aria-label="menyu">☰</button></div>
</div></nav>
<header class="hero"><div class="container">
  <div><h1>Issiq, mazali va <span style="color:var(--accent)">40 daqiqada</span> eshigingizda</h1>
  <p class="lead">Milliy taomlar, lavash, burger va shirinliklar. Saytda tanlang, bir tugma bilan buyurtma bering.</p>
  <a class="btn" href="#menyu">Menyuni ko'rish</a> <a class="btn ghost" href="#info">Manzil va ish vaqti</a></div>
  <div class="plate">🍜</div>
</div></header>
<section id="menyu"><div class="container">
  <h2>Menyu</h2><p class="muted">Narxlar so'mda. Savatga qo'shing va buyurtma bering.</p>
  <div class="tabs" id="tabs"></div>
  <div class="grid menu-grid" id="dishes"></div>
</div></section>
<section id="info" style="background:#fff"><div class="container">
  <h2>Biz haqimizda</h2>
  <div class="grid info" style="margin-top:18px">
    <div class="card"><b>📍 Manzil</b><p class="muted">Toshkent, Chilonzor 9-kvartal, 12-uy</p></div>
    <div class="card"><b>🕘 Ish vaqti</b><p class="muted">Har kuni 09:00 – 23:00</p></div>
    <div class="card"><b>🚚 Yetkazib berish</b><p class="muted">150 000 so'mdan bepul, aks holda 10 000 so'm</p></div>
  </div>
</div></section>
<section id="aloqa"><div class="container card" style="text-align:center">
  <h2>Savolingiz bormi?</h2><p class="muted">Qo'ng'iroq qiling yoki yozing</p>
  <p style="margin-top:14px"><a class="btn" href="tel:+998901234567">📞 +998 90 123 45 67</a></p>
</div></section>
<footer><div class="container">© 2026 Lazzat kafe</div></footer>
<aside class="drawer" id="drawer">
  <div style="display:flex;justify-content:space-between;align-items:center"><h3>Savat</h3><button class="btn ghost" onclick="toggleCart(false)">✕</button></div>
  <div id="cartItems"></div>
  <b>Jami: <span id="cartTotal">0</span></b>
  <input id="cName" placeholder="Ismingiz"><input id="cPhone" placeholder="Telefon" inputmode="tel"><input id="cAddr" placeholder="Manzil">
  <button class="btn" onclick="sendTelegram()">Telegram orqali buyurtma</button>
  <button class="btn ghost" onclick="sendWhatsApp()">WhatsApp orqali buyurtma</button>
</aside>
<div class="toast" id="toast"></div>
<script src="script.js"></script>
</body></html>
''')
w("sayt-kafe/script.js", CART_JS + '''
// Menyuni shu yerda tahrirlang: [id, toifa, nomi, tavsif, narx, emoji]
const DISHES = [
  ["d1", "Milliy", "Osh", "Qo'y go'shti, sariq sabzi, no'xat", 45000, "🍛"],
  ["d2", "Milliy", "Manti (5 dona)", "Bug'da pishgan, qaymoq bilan", 38000, "🥟"],
  ["d3", "Milliy", "Lag'mon", "Qo'lda cho'zilgan, mol go'shti", 40000, "🍜"],
  ["d4", "Fast-food", "Lavash", "Tovuq, pomidor, maxsus sous", 32000, "🌯"],
  ["d5", "Fast-food", "Burger", "Mol go'shti kotleti, pishloq", 35000, "🍔"],
  ["d6", "Fast-food", "Kartoshka fri", "Qarsildoq, katta porsiya", 15000, "🍟"],
  ["d7", "Ichimlik", "Ko'k choy (choynak)", "Limon bilan", 8000, "🫖"],
  ["d8", "Ichimlik", "Limonad 1L", "Uy limonadi, yalpiz", 18000, "🍋"],
  ["d9", "Shirinlik", "Medovik", "Asal tortidan bir bo'lak", 22000, "🍰"],
];
const cats = ["Hammasi", ...new Set(DISHES.map((d) => d[1]))];
let current = "Hammasi";
function renderMenu() {
  document.getElementById("tabs").innerHTML = cats.map((c) => `<button class="${c === current ? "on" : ""}" onclick="current='${c}';renderMenu()">${c}</button>`).join("");
  document.getElementById("dishes").innerHTML = DISHES.filter((d) => current === "Hammasi" || d[1] === current).map(([id, , n, t, p, e]) =>
    `<div class="card dish"><div class="em">${e}</div><b>${n}</b><span class="muted">${t}</span>
     <div class="row"><b>${fmt(p)}</b><button onclick="addToCart('${id}','${n.replace(/'/g, "\\\\'")}',${p})">+ Savatga</button></div></div>`).join("");
}
renderMenu();
''')

# ============================================================== S2 O'QUV MARKAZ
w("sayt-oquv-markaz/style.css", ":root{--bg:#f7f8ff;--card:#fff;--ink:#141a3a;--muted:#5d6488;--line:#e3e6f6;--accent:#4c5cff;--on-accent:#fff}\n" + BASE_CSS + '''
.hero{padding:80px 0 60px;background:linear-gradient(160deg,#eef0ff 0%,#f7f8ff 60%)}
.hero .container{display:grid;grid-template-columns:1.2fr .8fr;gap:30px;align-items:center}
.stats{display:flex;gap:28px;margin-top:30px;flex-wrap:wrap}.stats b{font-size:28px;display:block}
.board{background:#141a3a;color:#fff;border-radius:22px;padding:26px;font-family:ui-monospace,monospace;box-shadow:0 30px 60px rgba(20,26,58,.25)}
.board .ln{opacity:.85;margin:6px 0}.board .ok{color:#7cf29a}
.courses{grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}
.course .tag{display:inline-block;font-size:12px;padding:4px 10px;border-radius:99px;background:#eef0ff;color:var(--accent);font-weight:700}
.course h3{margin:10px 0 6px}.course ul{margin:10px 0 14px 18px;color:var(--muted);font-size:14px}
.price{font-size:22px;font-weight:800}
.steps{grid-template-columns:repeat(4,1fr)}.steps .n{width:36px;height:36px;border-radius:10px;background:var(--accent);color:#fff;display:grid;place-items:center;font-weight:800;margin-bottom:10px}
form.card{display:grid;gap:12px;max-width:520px}
form input,form select{padding:13px;border-radius:12px;border:1px solid var(--line);font-size:15px;background:#fff}
@media(max-width:760px){.hero .container{grid-template-columns:1fr}.steps{grid-template-columns:1fr 1fr}}
''')
w("sayt-oquv-markaz/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bilim+ o'quv markazi: IT, ingliz tili, matematika</title>
<meta name="description" content="Kichik guruhlar, amaliy darslar, bepul sinov darsi.">
<link rel="stylesheet" href="style.css"></head>
<body>
<nav class="nav"><div class="container">
  <a class="logo" href="#">🎓 Bilim<span style="color:var(--accent)">+</span></a>
  <div class="menu"><a href="#kurslar">Kurslar</a><a href="#qanday">Qanday o'qitamiz</a><a href="#yozilish">Yozilish</a></div>
  <div><a class="btn" href="#yozilish">Bepul sinov darsi</a> <button class="burger" aria-label="menyu">☰</button></div>
</div></nav>
<header class="hero"><div class="container">
  <div><h1>Kasb o'rganing, <span style="color:var(--accent)">natijani</span> ko'ring</h1>
  <p class="lead">IT, ingliz tili va matematika bo'yicha kichik guruhlarda amaliy darslar. Birinchi dars bepul.</p>
  <a class="btn" href="#yozilish">Sinov darsiga yozilish</a> <a class="btn ghost" href="#kurslar">Kurslar</a>
  <div class="stats"><div><b>8–12</b><span class="muted">kishilik guruh</span></div><div><b>3 oy</b><span class="muted">o'rtacha kurs</span></div><div><b>1-dars</b><span class="muted">bepul</span></div></div></div>
  <div class="board"><div class="ln">&gt; kurs.boshla("Python")</div><div class="ln">&gt; amaliyot: 70%</div><div class="ln">&gt; loyiha: portfolio uchun</div><div class="ln ok">✓ sertifikat tayyor</div></div>
</div></header>
<section id="kurslar"><div class="container">
  <h2>Kurslar</h2><p class="muted">Narxlar oylik. Har kursda amaliy loyiha bor.</p>
  <div class="grid courses" id="courseList" style="margin-top:20px"></div>
</div></section>
<section id="qanday" style="background:#fff"><div class="container">
  <h2>Qanday o'qitamiz</h2>
  <div class="grid steps" style="margin-top:20px">
    <div class="card"><div class="n">1</div><b>Bepul sinov darsi</b><p class="muted">Darajangizni aniqlaymiz</p></div>
    <div class="card"><div class="n">2</div><b>Kichik guruh</b><p class="muted">Har biriga e'tibor</p></div>
    <div class="card"><div class="n">3</div><b>Amaliy loyiha</b><p class="muted">Haqiqiy vazifalar</p></div>
    <div class="card"><div class="n">4</div><b>Sertifikat</b><p class="muted">Yakuniy imtihondan so'ng</p></div>
  </div>
</div></section>
<section id="yozilish"><div class="container">
  <h2>Sinov darsiga yozilish</h2><p class="muted" style="margin-bottom:16px">Ma'lumotingizni qoldiring, administrator bog'lanadi.</p>
  <form class="card" id="reg" onsubmit="return register(event)">
    <input id="rName" placeholder="Ism familiya" required>
    <input id="rPhone" placeholder="Telefon" inputmode="tel" required>
    <select id="rCourse"></select>
    <select id="rTime"><option>Ertalab (09:00–12:00)</option><option>Tushdan keyin (14:00–17:00)</option><option>Kechqurun (18:00–21:00)</option></select>
    <button class="btn" type="submit">Telegram orqali yuborish</button>
  </form>
</div></section>
<footer><div class="container">© 2026 Bilim+ o'quv markazi · Toshkent, Yunusobod · +998 90 123 45 67</div></footer>
<div class="toast" id="toast"></div>
<script src="script.js"></script>
</body></html>
''')
w("sayt-oquv-markaz/script.js", '''
// ====== SOZLAMALAR ======
const TG_USERNAME = "username"; // administrator Telegram username (@ belgisisiz)
// [nomi, toifa, oylik narx, davomiylik, nimalar o'rgatiladi]
const COURSES = [
  ["Python dasturlash", "IT", 600000, "4 oy", ["Asoslar va algoritmlar", "Telegram bot yaratish", "Yakuniy loyiha"]],
  ["Frontend (HTML, CSS, JS)", "IT", 650000, "5 oy", ["Moslashuvchan sayt", "JavaScript", "Portfolio sayt"]],
  ["Grafik dizayn", "IT", 550000, "3 oy", ["Figma, Photoshop", "Logo va banner", "SMM dizayn"]],
  ["Ingliz tili (General)", "Til", 450000, "6 oy", ["Grammatika", "Speaking club", "Darajaga qarab guruh"]],
  ["IELTS tayyorlov", "Til", 700000, "3 oy", ["4 ko'nikma", "Haftalik mock test", "Strategiyalar"]],
  ["Matematika (DTM)", "Fan", 400000, "6 oy", ["Nazariya + test", "Haftalik nazorat", "Ota-onaga hisobot"]],
];
// =========================
const fmt = (n) => n.toLocaleString("ru-RU").replace(/\\u00a0/g, " ") + " so'm";
function toast(t) { const el = document.getElementById("toast"); el.textContent = t; el.classList.add("show"); setTimeout(() => el.classList.remove("show"), 1800); }
document.getElementById("courseList").innerHTML = COURSES.map(([n, tag, p, d, list]) =>
  `<div class="card course"><span class="tag">${tag} · ${d}</span><h3>${n}</h3><ul>${list.map((x) => `<li>${x}</li>`).join("")}</ul>
   <div class="price">${fmt(p)}<span class="muted" style="font-size:14px;font-weight:400"> / oy</span></div>
   <a class="btn" style="margin-top:14px;width:100%" href="#yozilish" onclick="document.getElementById('rCourse').value='${n}'">Yozilish</a></div>`).join("");
document.getElementById("rCourse").innerHTML = COURSES.map((c) => `<option>${c[0]}</option>`).join("");
async function register(e) {
  e.preventDefault();
  const n = document.getElementById("rName").value.trim(), p = document.getElementById("rPhone").value.trim();
  if (!n || p.replace(/\\D/g, "").length < 9) { toast("Ism va telefonni to'g'ri kiriting"); return false; }
  const t = `📚 Sinov darsiga yozilish\\n👤 ${n}\\n📞 ${p}\\n📘 ${document.getElementById("rCourse").value}\\n🕘 ${document.getElementById("rTime").value}`;
  try { await navigator.clipboard.writeText(t); toast("Nusxalandi: Telegram'da yuboring"); } catch { prompt("Nusxa oling va yuboring:", t); }
  setTimeout(() => window.open(`https://t.me/${TG_USERNAME}`, "_blank"), 600);
  return false;
}
document.querySelector(".burger")?.addEventListener("click", () => document.querySelector(".menu").classList.toggle("open"));
''')

# ============================================================== S3 BARBERSHOP
w("sayt-barbershop/style.css", ":root{--bg:#0e0e10;--card:#17171b;--ink:#f3f1ec;--muted:#a19d94;--line:#2a2a30;--accent:#c9a45c;--on-accent:#111}\n" + BASE_CSS + '''
.hero{min-height:78vh;display:grid;align-items:center;background:radial-gradient(700px 380px at 80% 20%,rgba(201,164,92,.22),transparent),linear-gradient(180deg,#0e0e10,#141416)}
.hero h1 span{color:var(--accent)}
.svc{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.svc .card{display:flex;justify-content:space-between;align-items:center;gap:12px}
.svc .p{color:var(--accent);font-weight:800;white-space:nowrap}
.gal{grid-template-columns:repeat(4,1fr)}.gal div{aspect-ratio:3/4;border-radius:16px;background:linear-gradient(160deg,#2a2a30,#121214);display:grid;place-items:end start;padding:14px;font-size:13px;color:var(--muted);border:1px solid var(--line)}
.book{display:grid;gap:12px;max-width:560px}
.book select,.book input{padding:13px;border-radius:12px;border:1px solid var(--line);background:#0e0e10;color:var(--ink);font-size:15px}
.slots{display:flex;flex-wrap:wrap;gap:8px}.slots button{padding:9px 13px;border-radius:10px;border:1px solid var(--line);background:#0e0e10;color:var(--ink);cursor:pointer}
.slots button.on{background:var(--accent);color:#111;border-color:var(--accent)}
@media(max-width:760px){.gal{grid-template-columns:1fr 1fr}}
''')
w("sayt-barbershop/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>USTA barbershop: soch turmagi va soqol</title>
<meta name="description" content="Erkaklar sartaroshxonasi. Onlayn yozilish, navbatsiz.">
<link rel="stylesheet" href="style.css"></head>
<body>
<nav class="nav"><div class="container">
  <a class="logo" href="#">✂ USTA</a>
  <div class="menu"><a href="#xizmatlar">Xizmatlar</a><a href="#ishlar">Ishlar</a><a href="#yozilish">Yozilish</a></div>
  <div><a class="btn" href="#yozilish">Yozilish</a> <button class="burger" aria-label="menyu">☰</button></div>
</div></nav>
<header class="hero"><div class="container">
  <p class="muted" style="letter-spacing:.2em;font-size:13px">BARBERSHOP · TOSHKENT</p>
  <h1>Navbatsiz.<br>Aniq. <span>Ustalardan.</span></h1>
  <p class="lead">Soch turmagi, soqol dizayni va parvarish. Vaqtni onlayn tanlang, kelganingizda kutib o'tirmaysiz.</p>
  <a class="btn" href="#yozilish">Vaqt tanlash</a> <a class="btn ghost" href="#xizmatlar">Narxlar</a>
</div></header>
<section id="xizmatlar"><div class="container">
  <h2>Xizmatlar va narxlar</h2>
  <div class="grid svc" id="svcList" style="margin-top:20px"></div>
</div></section>
<section id="ishlar"><div class="container">
  <h2>Ishlarimiz</h2><p class="muted">Bu yerga o'z ishlaringiz rasmlarini qo'ying (README'ga qarang).</p>
  <div class="grid gal" style="margin-top:20px"><div>Fade</div><div>Klassika</div><div>Soqol dizayni</div><div>Bolalar</div></div>
</div></section>
<section id="yozilish"><div class="container">
  <h2>Onlayn yozilish</h2><p class="muted" style="margin-bottom:16px">Xizmat, kun va vaqtni tanlang.</p>
  <div class="card book">
    <select id="bSvc"></select>
    <input id="bDate" type="date">
    <div class="slots" id="slots"></div>
    <input id="bName" placeholder="Ismingiz"><input id="bPhone" placeholder="Telefon" inputmode="tel">
    <button class="btn" onclick="book()">Telegram orqali yozilish</button>
  </div>
</div></section>
<footer><div class="container">© 2026 USTA barbershop · Har kuni 10:00–21:00 · +998 90 123 45 67</div></footer>
<div class="toast" id="toast"></div>
<script src="script.js"></script>
</body></html>
''')
w("sayt-barbershop/script.js", '''
// ====== SOZLAMALAR ======
const TG_USERNAME = "username";
const SERVICES = [["Soch turmagi", 80000, "45 daq"], ["Soch + soqol", 120000, "70 daq"], ["Soqol dizayni", 50000, "30 daq"], ["Bolalar soch turmagi", 60000, "30 daq"], ["Soch bo'yash", 150000, "60 daq"], ["Yuz parvarishi", 70000, "30 daq"]];
const OPEN = 10, CLOSE = 21; // ish vaqti (soat)
// =========================
const fmt = (n) => n.toLocaleString("ru-RU").replace(/\\u00a0/g, " ") + " so'm";
let slot = "";
function toast(t) { const el = document.getElementById("toast"); el.textContent = t; el.classList.add("show"); setTimeout(() => el.classList.remove("show"), 1800); }
document.getElementById("svcList").innerHTML = SERVICES.map(([n, p, d]) => `<div class="card"><div><b>${n}</b><div class="muted">${d}</div></div><div class="p">${fmt(p)}</div></div>`).join("");
document.getElementById("bSvc").innerHTML = SERVICES.map(([n, p]) => `<option value="${n}">${n} · ${fmt(p)}</option>`).join("");
const dateEl = document.getElementById("bDate");
const today = new Date(); dateEl.min = today.toISOString().slice(0, 10); dateEl.value = dateEl.min;
function renderSlots() {
  const isToday = dateEl.value === dateEl.min; const now = new Date().getHours();
  const list = [];
  for (let h = OPEN; h < CLOSE; h++) for (const m of ["00", "30"]) if (!isToday || h > now) list.push(`${String(h).padStart(2, "0")}:${m}`);
  document.getElementById("slots").innerHTML = list.map((s) => `<button class="${s === slot ? "on" : ""}" onclick="slot='${s}';renderSlots()">${s}</button>`).join("") || '<span class="muted">Bugun uchun vaqt qolmadi, boshqa kunni tanlang.</span>';
}
dateEl.onchange = () => { slot = ""; renderSlots(); };
renderSlots();
async function book() {
  const n = document.getElementById("bName").value.trim(), p = document.getElementById("bPhone").value.trim();
  if (!slot) return toast("Vaqtni tanlang");
  if (!n || p.replace(/\\D/g, "").length < 9) return toast("Ism va telefonni kiriting");
  const t = `✂ Yozilish\\n💈 ${document.getElementById("bSvc").value}\\n📅 ${dateEl.value} ${slot}\\n👤 ${n}\\n📞 ${p}`;
  try { await navigator.clipboard.writeText(t); toast("Nusxalandi: Telegram'da yuboring"); } catch { prompt("Nusxa oling va yuboring:", t); }
  setTimeout(() => window.open(`https://t.me/${TG_USERNAME}`, "_blank"), 600);
}
document.querySelector(".burger")?.addEventListener("click", () => document.querySelector(".menu").classList.toggle("open"));
''')

# ============================================================== S4 PORTFOLIO
w("sayt-portfolio/style.css", ":root{--bg:#0b1020;--card:#121a33;--ink:#e8ecff;--muted:#9aa4c7;--line:#223055;--accent:#7c9cff;--on-accent:#0b1020}\n" + BASE_CSS + '''
.hero{min-height:82vh;display:grid;align-items:center}
.hero .avatar{width:120px;height:120px;border-radius:30px;background:linear-gradient(135deg,#7c9cff,#b388ff);display:grid;place-items:center;font-size:52px;margin-bottom:24px;box-shadow:0 20px 50px rgba(124,156,255,.35)}
.hero h1 span{background:linear-gradient(90deg,#7c9cff,#b388ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.skills{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.skills span{padding:8px 14px;border-radius:99px;border:1px solid var(--line);font-size:14px;color:var(--muted)}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.filters button{padding:8px 14px;border-radius:99px;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer}
.filters button.on{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}
.works{grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.work .thumb{height:170px;border-radius:14px;margin-bottom:14px;display:grid;place-items:center;font-size:44px}
.work .tags{font-size:13px;color:var(--accent);margin-top:8px}
.timeline .card{border-left:3px solid var(--accent)}
''')
w("sayt-portfolio/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aziz Karimov: frontend dasturchi</title>
<meta name="description" content="Moslashuvchan saytlar, Telegram botlar va veb-ilovalar.">
<link rel="stylesheet" href="style.css"></head>
<body>
<nav class="nav"><div class="container">
  <a class="logo" href="#">AK<span style="color:var(--accent)">.</span></a>
  <div class="menu"><a href="#ishlar">Ishlar</a><a href="#tajriba">Tajriba</a><a href="#aloqa">Aloqa</a></div>
  <div><a class="btn" href="#aloqa">Bog'lanish</a> <button class="burger" aria-label="menyu">☰</button></div>
</div></nav>
<header class="hero"><div class="container">
  <div class="avatar">👨‍💻</div>
  <h1>Salom, men Aziz.<br><span>Biznes uchun sayt va botlar</span> yarataman.</h1>
  <p class="lead">4 yillik tajriba: landing sahifalar, internet do'konlar, Telegram botlar. Tez, toza kod va aniq muddat.</p>
  <a class="btn" href="#ishlar">Ishlarimni ko'rish</a> <a class="btn ghost" href="#aloqa">Loyiha muhokamasi</a>
  <div class="skills"><span>HTML/CSS</span><span>JavaScript</span><span>React</span><span>Python</span><span>Telegram Bot API</span><span>Figma</span></div>
</div></header>
<section id="ishlar"><div class="container">
  <h2>Tanlangan ishlar</h2>
  <div class="filters" id="filters"></div>
  <div class="grid works" id="works"></div>
</div></section>
<section id="tajriba"><div class="container">
  <h2>Tajriba</h2>
  <div class="grid timeline" style="margin-top:18px">
    <div class="card"><b>Frontend dasturchi · Kompaniya nomi</b><p class="muted">2024 – hozir · Korporativ saytlar va ichki tizimlar</p></div>
    <div class="card"><b>Freelancer</b><p class="muted">2022 – 2024 · 30+ kichik biznes loyihasi</p></div>
  </div>
</div></section>
<section id="aloqa"><div class="container card" style="text-align:center">
  <h2>Loyihangiz bormi?</h2><p class="muted">Qisqacha yozing, 24 soat ichida javob beraman.</p>
  <p style="margin-top:16px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap"><a class="btn" href="https://t.me/username">Telegram</a><a class="btn ghost" href="mailto:mail@example.com">Email</a></p>
</div></section>
<footer><div class="container">© 2026 Aziz Karimov</div></footer>
<script src="script.js"></script>
</body></html>
''')
w("sayt-portfolio/script.js", '''
// Ishlaringizni shu yerda tahrirlang: [nomi, toifa, tavsif, texnologiyalar, emoji, rang, havola]
const WORKS = [
  ["Restoran sayti", "Sayt", "Onlayn menyu va buyurtma", "HTML, CSS, JS", "🍽", "#2b3a67", "#"],
  ["Do'kon katalogi", "Sayt", "Savat, filtr, WhatsApp buyurtma", "JavaScript", "🛍", "#3d2b67", "#"],
  ["Buyurtma boti", "Bot", "Menyu, savat, admin panel", "Python", "🤖", "#1f4d4a", "#"],
  ["CRM dashboard", "Ilova", "Mijozlar va sotuv grafiklari", "React", "📊", "#4d3a1f", "#"],
  ["O'quv markaz lendingi", "Sayt", "Kurslar va yozilish formasi", "HTML, CSS", "🎓", "#1f3a4d", "#"],
  ["Navbat boti", "Bot", "Sartaroshxona uchun onlayn yozilish", "Python", "✂", "#4d1f3a", "#"],
];
const cats = ["Hammasi", ...new Set(WORKS.map((w) => w[1]))];
let cur = "Hammasi";
function render() {
  document.getElementById("filters").innerHTML = cats.map((c) => `<button class="${c === cur ? "on" : ""}" onclick="cur='${c}';render()">${c}</button>`).join("");
  document.getElementById("works").innerHTML = WORKS.filter((w) => cur === "Hammasi" || w[1] === cur).map(([n, c, d, t, e, col, href]) =>
    `<a class="card work" href="${href}"><div class="thumb" style="background:linear-gradient(135deg,${col},#121a33)">${e}</div><b>${n}</b><p class="muted">${d}</p><div class="tags">${t}</div></a>`).join("");
}
render();
document.querySelector(".burger")?.addEventListener("click", () => document.querySelector(".menu").classList.toggle("open"));
''')

# ============================================================== S5 DO'KON KATALOG
w("sayt-dokon/style.css", ":root{--bg:#f6f7f9;--card:#fff;--ink:#111827;--muted:#6b7280;--line:#e5e7eb;--accent:#16a34a;--on-accent:#fff}\n" + BASE_CSS + CART_CSS + '''
.hero{padding:46px 0 10px}
.bar{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
.bar input,.bar select{padding:12px;border-radius:12px;border:1px solid var(--line);font-size:15px;background:#fff}
.bar input{flex:1;min-width:200px}
.products{grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
.prod{padding:14px;display:flex;flex-direction:column;gap:6px}
.prod .ph{height:150px;border-radius:12px;display:grid;place-items:center;font-size:56px;background:#f1f5f9}
.prod .old{text-decoration:line-through;color:var(--muted);font-size:13px;margin-left:6px}
.prod .badge{align-self:flex-start;background:#fee2e2;color:#b91c1c;font-size:12px;font-weight:700;padding:3px 8px;border-radius:99px}
.prod button{margin-top:auto;padding:10px;border-radius:10px;border:0;background:var(--accent);color:#fff;font-weight:700;cursor:pointer}
.empty{padding:40px;text-align:center;color:var(--muted)}
''')
w("sayt-dokon/index.html", '''
<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GadgetUz: aksessuarlar internet do'koni</title>
<meta name="description" content="Telefon aksessuarlari, quloqchinlar, zaryadlovchilar. Yetkazib berish butun O'zbekiston bo'ylab.">
<link rel="stylesheet" href="style.css"></head>
<body>
<nav class="nav"><div class="container">
  <a class="logo" href="#">🛍 Gadget<span style="color:var(--accent)">Uz</span></a>
  <div class="menu"><a href="#katalog">Katalog</a><a href="#yetkazish">Yetkazib berish</a></div>
  <div style="display:flex;gap:8px;align-items:center"><button class="btn cartbtn" onclick="toggleCart(true)">🛒<span id="cartCount">0</span></button><button class="burger" aria-label="menyu">☰</button></div>
</div></nav>
<header class="hero"><div class="container">
  <h1 style="font-size:clamp(30px,5vw,46px)">Aksessuarlar: arzon, sifatli, <span style="color:var(--accent)">bugun yetkaziladi</span></h1>
  <p class="lead">Toshkent bo'ylab 3 soatda, viloyatlarga 1–3 kunda. Tanlang va bir tugma bilan buyurtma bering.</p>
</div></header>
<section id="katalog" style="padding-top:10px"><div class="container">
  <div class="bar"><input id="q" placeholder="Qidirish: quloqchin, kabel..."><select id="cat"></select><select id="sort"><option value="pop">Ommabop</option><option value="asc">Avval arzon</option><option value="desc">Avval qimmat</option></select></div>
  <div class="grid products" id="products"></div>
</div></section>
<section id="yetkazish" style="background:#fff"><div class="container grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">
  <div class="card"><b>🚚 Toshkent</b><p class="muted">3 soat ichida, 20 000 so'm. 300 000 so'mdan bepul.</p></div>
  <div class="card"><b>📦 Viloyatlar</b><p class="muted">Pochta orqali 1–3 kun.</p></div>
  <div class="card"><b>💳 To'lov</b><p class="muted">Naqd, Click, Payme yoki karta orqali.</p></div>
  <div class="card"><b>🔄 Qaytarish</b><p class="muted">Nuqsonli mahsulot 14 kun ichida almashtiriladi.</p></div>
</div></section>
<footer><div class="container">© 2026 GadgetUz · +998 90 123 45 67</div></footer>
<aside class="drawer" id="drawer">
  <div style="display:flex;justify-content:space-between;align-items:center"><h3>Savat</h3><button class="btn ghost" onclick="toggleCart(false)">✕</button></div>
  <div id="cartItems"></div>
  <b>Jami: <span id="cartTotal">0</span></b>
  <input id="cName" placeholder="Ismingiz"><input id="cPhone" placeholder="Telefon" inputmode="tel"><input id="cAddr" placeholder="Shahar, manzil">
  <button class="btn" onclick="sendTelegram()">Telegram orqali buyurtma</button>
  <button class="btn ghost" onclick="sendWhatsApp()">WhatsApp orqali buyurtma</button>
</aside>
<div class="toast" id="toast"></div>
<script src="script.js"></script>
</body></html>
''')
w("sayt-dokon/script.js", CART_JS + '''
// Mahsulotlar: [id, toifa, nomi, narx, eski narx (yoki 0), emoji, ommaboplik]
const PRODUCTS = [
  ["p1", "Quloqchin", "Simsiz quloqchin TWS Pro", 249000, 320000, "🎧", 98],
  ["p2", "Quloqchin", "Simli quloqchin Type-C", 59000, 0, "🎧", 70],
  ["p3", "Zaryadlovchi", "Tez zaryadlovchi 33W", 129000, 159000, "🔌", 95],
  ["p4", "Zaryadlovchi", "Powerbank 20 000 mAh", 289000, 0, "🔋", 90],
  ["p5", "Kabel", "Kabel Type-C 1 m (kuchaytirilgan)", 39000, 0, "🧵", 85],
  ["p6", "Kabel", "Kabel Lightning 2 m", 49000, 0, "🧵", 60],
  ["p7", "Himoya", "Himoya oynasi (2 dona)", 35000, 50000, "🛡", 88],
  ["p8", "Himoya", "Silikon g'ilof", 45000, 0, "📱", 75],
  ["p9", "Boshqa", "Avtomobil ushlagichi", 79000, 0, "🚗", 55],
  ["p10", "Boshqa", "Aqlli soat Fit", 399000, 499000, "⌚", 80],
];
const catEl = document.getElementById("cat"), qEl = document.getElementById("q"), sortEl = document.getElementById("sort");
catEl.innerHTML = ["Hammasi", ...new Set(PRODUCTS.map((p) => p[1]))].map((c) => `<option>${c}</option>`).join("");
function renderProducts() {
  const q = qEl.value.trim().toLowerCase(), c = catEl.value;
  let list = PRODUCTS.filter((p) => (c === "Hammasi" || p[1] === c) && p[2].toLowerCase().includes(q));
  list.sort((a, b) => sortEl.value === "asc" ? a[3] - b[3] : sortEl.value === "desc" ? b[3] - a[3] : b[6] - a[6]);
  document.getElementById("products").innerHTML = list.map(([id, , n, p, old, e]) =>
    `<div class="card prod">${old ? `<span class="badge">-${Math.round((1 - p / old) * 100)}%</span>` : ""}<div class="ph">${e}</div><b>${n}</b>
     <div><b>${fmt(p)}</b>${old ? `<span class="old">${fmt(old)}</span>` : ""}</div>
     <button onclick="addToCart('${id}','${n.replace(/'/g, "\\\\'")}',${p})">Savatga</button></div>`).join("") || '<div class="empty">Hech narsa topilmadi</div>';
}
[qEl, catEl, sortEl].forEach((el) => el.addEventListener("input", renderProducts));
renderProducts();
''')

README = '''
# {title}

Tayyor, moslashuvchan (telefon va kompyuterga mos) sayt shabloni. Hech qanday kutubxona va internet kerak emas: oddiy HTML, CSS, JavaScript.

## Ichida
{features}

## Ochib ko'rish
`index.html` faylini ikki marta bosing, brauzerda ochiladi.

## O'zingizga moslash
1. **Matnlar:** `index.html` ni Bloknot yoki VS Code'da oching, matnlarni almashtiring (nom, manzil, telefon).
2. **{data_hint}:** `script.js` ning tepasidagi ro'yxatni tahrirlang.
3. **Telegram/WhatsApp:** `script.js` tepasidagi `TG_USERNAME` (va bor bo'lsa `PHONE`) ni o'zingiznikiga almashtiring.
4. **Ranglar:** `style.css` ning birinchi qatoridagi `--accent` (asosiy rang) va `--bg` (fon) qiymatlarini o'zgartiring.
5. **Rasmlar:** emoji o'rniga rasm qo'yish uchun `img` papka yarating, rasmni tashlang va kerakli joyga `<img src="img/rasm.jpg" alt="">` yozing.

## Internetga joylash (bepul)
- **Netlify Drop:** app.netlify.com/drop sahifasiga papkani sudrab tashlang, 30 soniyada sayt tayyor.
- **GitHub Pages:** GitHub'da repozitoriy oching, fayllarni yuklang, Settings → Pages → Deploy from branch.
- O'z domeningiz (.uz) bo'lsa, Netlify/GitHub sozlamalarida ulaysiz.
'''
for slug, title, feats, hint in [
    ("sayt-kafe", "Kafe / restoran sayti (onlayn menyu + savat)", "- Toifali menyu (filtr bilan)\n- Savat, miqdorni o'zgartirish, jami summa\n- Buyurtmani Telegram yoki WhatsApp orqali yuborish\n- Manzil, ish vaqti, yetkazib berish shartlari", "Menyu"),
    ("sayt-oquv-markaz", "O'quv markazi sayti (kurslar + yozilish)", "- Kurslar kartochkalari (narx, davomiylik, mavzular)\n- «Qanday o'qitamiz» bloki\n- Sinov darsiga yozilish formasi (Telegram'ga)", "Kurslar"),
    ("sayt-barbershop", "Barbershop / salon sayti (onlayn yozilish)", "- Xizmatlar va narxlar\n- Ishlar galereyasi (o'z rasmlaringizni qo'yasiz)\n- Kun va vaqt tanlab yozilish (o'tgan vaqtlar ko'rinmaydi)", "Xizmatlar va ish vaqti"),
    ("sayt-portfolio", "Shaxsiy portfolio sayti (dasturchi, dizayner, SMM)", "- Qorong'i zamonaviy dizayn\n- Ishlar ro'yxati, toifa bo'yicha filtr\n- Tajriba va aloqa bloki", "Ishlar ro'yxati"),
    ("sayt-dokon", "Internet do'kon katalogi (savat + buyurtma)", "- Qidiruv, toifa filtri, narx bo'yicha saralash\n- Chegirma belgisi va eski narx\n- Savat va Telegram/WhatsApp orqali buyurtma", "Mahsulotlar"),
]:
    w(f"{slug}/README.md", README.format(title=title, features=feats, data_hint=hint))
print("ok sites")
