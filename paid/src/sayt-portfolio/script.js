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
