// ====== SOZLAMALAR ======
const TG_USERNAME = "username";
const SERVICES = [["Soch turmagi", 80000, "45 daq"], ["Soch + soqol", 120000, "70 daq"], ["Soqol dizayni", 50000, "30 daq"], ["Bolalar soch turmagi", 60000, "30 daq"], ["Soch bo'yash", 150000, "60 daq"], ["Yuz parvarishi", 70000, "30 daq"]];
const OPEN = 10, CLOSE = 21; // ish vaqti (soat)
// =========================
const fmt = (n) => n.toLocaleString("ru-RU").replace(/\u00a0/g, " ") + " so'm";
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
  if (!n || p.replace(/\D/g, "").length < 9) return toast("Ism va telefonni kiriting");
  const t = `✂ Yozilish\n💈 ${document.getElementById("bSvc").value}\n📅 ${dateEl.value} ${slot}\n👤 ${n}\n📞 ${p}`;
  try { await navigator.clipboard.writeText(t); toast("Nusxalandi: Telegram'da yuboring"); } catch { prompt("Nusxa oling va yuboring:", t); }
  setTimeout(() => window.open(`https://t.me/${TG_USERNAME}`, "_blank"), 600);
}
document.querySelector(".burger")?.addEventListener("click", () => document.querySelector(".menu").classList.toggle("open"));
