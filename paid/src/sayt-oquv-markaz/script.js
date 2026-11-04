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
const fmt = (n) => n.toLocaleString("ru-RU").replace(/\u00a0/g, " ") + " so'm";
function toast(t) { const el = document.getElementById("toast"); el.textContent = t; el.classList.add("show"); setTimeout(() => el.classList.remove("show"), 1800); }
document.getElementById("courseList").innerHTML = COURSES.map(([n, tag, p, d, list]) =>
  `<div class="card course"><span class="tag">${tag} · ${d}</span><h3>${n}</h3><ul>${list.map((x) => `<li>${x}</li>`).join("")}</ul>
   <div class="price">${fmt(p)}<span class="muted" style="font-size:14px;font-weight:400"> / oy</span></div>
   <a class="btn" style="margin-top:14px;width:100%" href="#yozilish" onclick="document.getElementById('rCourse').value='${n}'">Yozilish</a></div>`).join("");
document.getElementById("rCourse").innerHTML = COURSES.map((c) => `<option>${c[0]}</option>`).join("");
async function register(e) {
  e.preventDefault();
  const n = document.getElementById("rName").value.trim(), p = document.getElementById("rPhone").value.trim();
  if (!n || p.replace(/\D/g, "").length < 9) { toast("Ism va telefonni to'g'ri kiriting"); return false; }
  const t = `📚 Sinov darsiga yozilish\n👤 ${n}\n📞 ${p}\n📘 ${document.getElementById("rCourse").value}\n🕘 ${document.getElementById("rTime").value}`;
  try { await navigator.clipboard.writeText(t); toast("Nusxalandi: Telegram'da yuboring"); } catch { prompt("Nusxa oling va yuboring:", t); }
  setTimeout(() => window.open(`https://t.me/${TG_USERNAME}`, "_blank"), 600);
  return false;
}
document.querySelector(".burger")?.addEventListener("click", () => document.querySelector(".menu").classList.toggle("open"));
