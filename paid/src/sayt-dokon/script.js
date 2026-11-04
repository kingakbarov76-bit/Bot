// ====== SOZLAMALAR: o'zingiznikiga almashtiring ======
const PHONE = "998901234567";      // WhatsApp raqam (faqat raqamlar)
const TG_USERNAME = "username";    // Telegram username (@ belgisisiz)
// ====================================================
const cart = {};
const fmt = (n) => n.toLocaleString("ru-RU").replace(/\u00a0/g, " ") + " so'm";
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
    : '<p class="muted">Savat bo\'sh</p>';
  document.getElementById("cartTotal").textContent = fmt(cartTotal());
}
function orderText() {
  const name = document.getElementById("cName").value.trim(), phone = document.getElementById("cPhone").value.trim(), addr = document.getElementById("cAddr").value.trim();
  if (!Object.keys(cart).length) { toast("Savat bo'sh"); return null; }
  if (!name || phone.replace(/\D/g, "").length < 9) { toast("Ism va telefonni kiriting"); return null; }
  const lines = Object.values(cart).map((x) => `• ${x.name} × ${x.qty} = ${fmt(x.price * x.qty)}`);
  return `🛒 Buyurtma\n${lines.join("\n")}\nJami: ${fmt(cartTotal())}\n\n👤 ${name}\n📞 ${phone}\n📍 ${addr || "-"}`;
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
     <button onclick="addToCart('${id}','${n.replace(/'/g, "\\'")}',${p})">Savatga</button></div>`).join("") || '<div class="empty">Hech narsa topilmadi</div>';
}
[qEl, catEl, sortEl].forEach((el) => el.addEventListener("input", renderProducts));
renderProducts();
