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
     <div class="row"><b>${fmt(p)}</b><button onclick="addToCart('${id}','${n.replace(/'/g, "\\'")}',${p})">+ Savatga</button></div></div>`).join("");
}
renderMenu();
