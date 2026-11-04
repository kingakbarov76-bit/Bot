# 5 ta dizayn shabloni: brauzerda tahrirlanadi va PNG (yoki PDF) qilib yuklab olinadi. Internet kerak emas.
import os, textwrap, json
B = "/home/claude/bot/paid/src"
def w(path, s):
    p = os.path.join(B, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(textwrap.dedent(s).lstrip("\n"))

ENGINE = '''
// Shablon dvigateli: maydonlar -> SVG matni/ranglari, PNG yuklab olish, chop etish (PDF).
function bindTemplate(svgId) {
  const svg = document.getElementById(svgId);
  document.querySelectorAll("[data-text]").forEach((inp) => {
    const upd = () => svg.querySelectorAll(`[data-k="${inp.dataset.text}"]`).forEach((n) => (n.textContent = inp.value));
    inp.addEventListener("input", upd); upd();
  });
  document.querySelectorAll("[data-color]").forEach((inp) => {
    const upd = () => svg.querySelectorAll(`[data-c="${inp.dataset.color}"]`).forEach((n) => {
      const attr = n.dataset.attr || "fill"; n.setAttribute(attr, inp.value);
    });
    inp.addEventListener("input", upd); upd();
  });
}
function svgToPng(svgId, fileName, scale = 1) {
  const svg = document.getElementById(svgId);
  const w = Number(svg.getAttribute("width")), h = Number(svg.getAttribute("height"));
  const xml = new XMLSerializer().serializeToString(svg);
  const img = new Image();
  img.onload = () => {
    const c = document.createElement("canvas"); c.width = w * scale; c.height = h * scale;
    const ctx = c.getContext("2d"); ctx.scale(scale, scale); ctx.drawImage(img, 0, 0, w, h);
    c.toBlob((b) => { const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = fileName; a.click(); }, "image/png");
  };
  img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(xml);
}
function svgDownload(svgId, fileName) {
  const xml = new XMLSerializer().serializeToString(document.getElementById(svgId));
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([xml], { type: "image/svg+xml" })); a.download = fileName; a.click();
}
'''

PAGE = '''
<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{box-sizing:border-box;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}}
body{{margin:0;background:#eef1f5;color:#111}}
.app{{display:grid;grid-template-columns:330px 1fr;min-height:100vh}}
.side{{background:#fff;padding:18px;border-right:1px solid #e3e6ec;overflow:auto}}
.side h1{{font-size:18px;margin:0 0 4px}} .side p{{color:#667;font-size:13px;margin:0 0 14px}}
label{{display:block;font-size:13px;color:#445;margin:10px 0 4px}}
input[type=text],textarea{{width:100%;padding:10px;border:1px solid #d5d9e2;border-radius:9px;font-size:14px}}
input[type=color]{{width:44px;height:34px;border:0;background:none;padding:0}}
.colors{{display:flex;gap:14px;flex-wrap:wrap}} .colors label{{margin:6px 0}}
.btns{{display:grid;gap:8px;margin-top:16px}}
button{{padding:12px;border-radius:10px;border:0;background:#111;color:#fff;font-weight:700;cursor:pointer;font-size:14px}}
button.alt{{background:#e9ecf2;color:#111}}
.stage{{display:grid;place-items:start center;padding:24px;overflow:auto}}
.stage svg{{position:sticky;top:24px;width:min(100%,{pw}px);height:auto;box-shadow:0 20px 50px rgba(0,0,0,.15);background:#fff}}
@media(max-width:820px){{.app{{grid-template-columns:1fr}}.side{{border-right:0;border-bottom:1px solid #e3e6ec}}}}
@media print{{body{{background:#fff}}.side{{display:none}}.app{{display:block}}.stage{{padding:0}}.stage svg{{width:100%;box-shadow:none}}@page{{size:{page};margin:0}}}}
</style></head>
<body>
<div class="app">
<div class="side">
<h1>{title}</h1><p>Maydonlarni o'zgartiring, o'ngda darhol ko'rinadi. Tayyor bo'lgach yuklab oling.</p>
{fields}
<div class="btns">{buttons}</div>
<p style="margin-top:14px">💡 SVG faylni Figma, Canva yoki Inkscape'da ochib, yanada erkin tahrirlash mumkin.</p>
</div>
<div class="stage">{svg}</div>
</div>
<script src="engine.js"></script>
<script>bindTemplate("tpl");</script>
</body></html>
'''

def field(k, label, val, area=False):
    v = val.replace('"', "&quot;")
    return f'<label>{label}</label><input type="text" data-text="{k}" value="{v}">'
def colors(items):
    return '<div class="colors">' + "".join(f'<label>{l}<br><input type="color" data-color="{k}" value="{v}"></label>' for k, l, v in items) + "</div>"

def make(slug, title, svg, fields, pw, page, png_name, scale, extra_buttons=""):
    buttons = (f'<button onclick="svgToPng(\'tpl\',\'{png_name}\',{scale})">⬇ PNG yuklab olish</button>'
               f'<button class="alt" onclick="svgDownload(\'tpl\',\'{png_name.replace(".png", ".svg")}\')">⬇ SVG (tahrirlash uchun)</button>' + extra_buttons)
    w(f"{slug}/index.html", PAGE.format(title=title, fields=fields, buttons=buttons, svg=svg, pw=pw, page=page))
    w(f"{slug}/engine.js", ENGINE)

F = 'font-family="Segoe UI, Roboto, Arial, sans-serif"'

# ---------------------------------------------------------------- D1 Instagram aksiya posti 1080x1080
svg1 = f'''<svg id="tpl" xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080" {F}>
<rect width="1080" height="1080" data-c="bg" fill="#111827"/>
<circle cx="900" cy="170" r="300" data-c="accent" fill="#f97316" opacity=".9"/>
<circle cx="1000" cy="1010" r="230" data-c="accent2" fill="#facc15" opacity=".85"/>
<text x="80" y="150" font-size="38" font-weight="700" fill="#fff" opacity=".8" data-k="brand">@dokonim</text>
<text x="80" y="420" font-size="120" font-weight="900" fill="#fff" data-k="t1">KATTA</text>
<text x="80" y="540" font-size="120" font-weight="900" fill="#fff" data-k="t2">CHEGIRMA</text>
<rect x="80" y="600" width="520" height="160" rx="28" data-c="accent" fill="#f97316"/>
<text x="340" y="712" font-size="104" font-weight="900" fill="#111" text-anchor="middle" data-k="pct">-50%</text>
<text x="80" y="850" font-size="44" fill="#fff" data-k="sub">Barcha mahsulotlarga</text>
<text x="80" y="910" font-size="36" fill="#fff" opacity=".75" data-k="date">1–10 dekabr</text>
</svg>'''
make("dizayn-instagram-aksiya", "Instagram aksiya posti (1080×1080)", svg1,
     field("brand", "Brend / sahifa", "@dokonim") + field("t1", "Sarlavha 1-qator", "KATTA") + field("t2", "Sarlavha 2-qator", "CHEGIRMA") +
     field("pct", "Chegirma", "-50%") + field("sub", "Izoh", "Barcha mahsulotlarga") + field("date", "Muddat", "1–10 dekabr") +
     colors([("bg", "Fon", "#111827"), ("accent", "Asosiy", "#f97316"), ("accent2", "Qo'shimcha", "#facc15")]),
     560, "1080px 1080px", "aksiya-post.png", 1)

# ---------------------------------------------------------------- D2 Vizitka 1050x600 (90x50 mm @ ~300dpi)
svg2 = f'''<svg id="tpl" xmlns="http://www.w3.org/2000/svg" width="1063" height="591" viewBox="0 0 1063 591" {F}>
<rect width="1063" height="591" fill="#ffffff"/>
<rect width="330" height="591" data-c="side" fill="#1e3a8a"/>
<text x="165" y="300" font-size="120" font-weight="900" fill="#fff" text-anchor="middle" data-k="ini">AK</text>
<text x="165" y="370" font-size="26" fill="#fff" opacity=".8" text-anchor="middle" data-k="company">KOMPANIYA</text>
<text x="390" y="170" font-size="58" font-weight="800" data-c="ink" fill="#0f172a" data-k="name">Aziz Karimov</text>
<text x="390" y="225" font-size="32" data-c="side" fill="#1e3a8a" data-k="role">Marketing menejeri</text>
<rect x="390" y="262" width="90" height="6" rx="3" data-c="side" fill="#1e3a8a"/>
<text x="390" y="340" font-size="30" fill="#334155" data-k="phone">📞 +998 90 123 45 67</text>
<text x="390" y="395" font-size="30" fill="#334155" data-k="mail">✉ aziz@kompaniya.uz</text>
<text x="390" y="450" font-size="30" fill="#334155" data-k="tg">✈ t.me/aziz_k</text>
<text x="390" y="505" font-size="30" fill="#334155" data-k="addr">📍 Toshkent, Yunusobod</text>
</svg>'''
make("dizayn-vizitka", "Vizitka shabloni (90×50 mm, chop etishga tayyor)", svg2,
     field("name", "Ism familiya", "Aziz Karimov") + field("role", "Lavozim", "Marketing menejeri") + field("ini", "Bosh harflar / logo", "AK") +
     field("company", "Kompaniya", "KOMPANIYA") + field("phone", "Telefon", "📞 +998 90 123 45 67") + field("mail", "Email", "✉ aziz@kompaniya.uz") +
     field("tg", "Telegram / sayt", "✈ t.me/aziz_k") + field("addr", "Manzil", "📍 Toshkent, Yunusobod") +
     colors([("side", "Asosiy rang", "#1e3a8a"), ("ink", "Ism rangi", "#0f172a")]),
     760, "90mm 50mm", "vizitka.png", 1, '<button class="alt" onclick="window.print()">🖨 PDF / chop etish</button>')

# ---------------------------------------------------------------- D3 Sertifikat A4 landscape (1754x1240)
svg3 = f'''<svg id="tpl" xmlns="http://www.w3.org/2000/svg" width="1754" height="1240" viewBox="0 0 1754 1240" {F}>
<rect width="1754" height="1240" fill="#fffdf7"/>
<rect x="40" y="40" width="1674" height="1160" fill="none" stroke-width="14" data-c="gold" data-attr="stroke" stroke="#b8892b"/>
<rect x="72" y="72" width="1610" height="1096" fill="none" stroke-width="3" data-c="gold" data-attr="stroke" stroke="#b8892b"/>
<text x="877" y="250" font-size="40" letter-spacing="10" text-anchor="middle" fill="#6b5b3e" data-k="org">BILIM+ O'QUV MARKAZI</text>
<text x="877" y="400" font-size="130" font-weight="800" text-anchor="middle" data-c="ink" fill="#1f2937" data-k="title">SERTIFIKAT</text>
<text x="877" y="490" font-size="38" text-anchor="middle" fill="#6b7280" data-k="given">Ushbu sertifikat</text>
<text x="877" y="610" font-size="92" font-weight="700" font-style="italic" text-anchor="middle" data-c="gold" fill="#b8892b" data-k="name">Ism Familiya</text>
<line x1="477" y1="650" x2="1277" y2="650" stroke="#d6c7a1" stroke-width="3"/>
<text x="877" y="730" font-size="38" text-anchor="middle" fill="#374151" data-k="line1">«Python dasturlash» kursini muvaffaqiyatli</text>
<text x="877" y="785" font-size="38" text-anchor="middle" fill="#374151" data-k="line2">tamomlagani uchun berildi</text>
<text x="420" y="1010" font-size="32" text-anchor="middle" fill="#374151" data-k="date">04.11.2026</text>
<line x1="270" y1="1030" x2="570" y2="1030" stroke="#9ca3af" stroke-width="2"/>
<text x="420" y="1070" font-size="26" text-anchor="middle" fill="#9ca3af">Sana</text>
<text x="1334" y="1010" font-size="32" text-anchor="middle" fill="#374151" data-k="sign">Direktor: A. Karimov</text>
<line x1="1184" y1="1030" x2="1484" y2="1030" stroke="#9ca3af" stroke-width="2"/>
<text x="1334" y="1070" font-size="26" text-anchor="middle" fill="#9ca3af">Imzo</text>
<circle cx="877" cy="1010" r="80" fill="none" stroke-width="6" data-c="gold" data-attr="stroke" stroke="#b8892b"/>
<text x="877" y="1025" font-size="44" font-weight="800" text-anchor="middle" data-c="gold" fill="#b8892b" data-k="seal">№ 001</text>
</svg>'''
make("dizayn-sertifikat", "Sertifikat / diplom shabloni (A4)", svg3,
     field("org", "Tashkilot", "BILIM+ O'QUV MARKAZI") + field("title", "Sarlavha", "SERTIFIKAT") + field("given", "Kirish so'zi", "Ushbu sertifikat") +
     field("name", "Ism familiya", "Ism Familiya") + field("line1", "Matn 1-qator", "«Python dasturlash» kursini muvaffaqiyatli") +
     field("line2", "Matn 2-qator", "tamomlagani uchun berildi") + field("date", "Sana", "04.11.2026") + field("sign", "Imzo qo'yuvchi", "Direktor: A. Karimov") +
     field("seal", "Raqam", "№ 001") + colors([("gold", "Bezak rangi", "#b8892b"), ("ink", "Sarlavha rangi", "#1f2937")]),
     1000, "A4 landscape", "sertifikat.png", 1, '<button class="alt" onclick="window.print()">🖨 PDF / chop etish</button>')

# ---------------------------------------------------------------- D4 Narxlar ro'yxati / menyu A4 portrait (1240x1754)
rows = [("Soch turmagi", "80 000"), ("Soch + soqol", "120 000"), ("Soqol dizayni", "50 000"), ("Bolalar soch turmagi", "60 000"),
        ("Soch bo'yash", "150 000"), ("Yuz parvarishi", "70 000"), ("Massaj (15 daq)", "40 000"), ("Ukladka", "30 000")]
items = ""; flds = ""
for i, (n, p) in enumerate(rows):
    y = 560 + i * 120
    items += (f'<text x="140" y="{y}" font-size="44" fill="#e5e7eb" data-k="n{i}">{n}</text>'
              f'<line x1="140" y1="{y + 34}" x2="1100" y2="{y + 34}" stroke="#374151" stroke-width="2" stroke-dasharray="6 10"/>'
              f'<text x="1100" y="{y}" font-size="44" font-weight="800" text-anchor="end" data-c="accent" fill="#d4a24c" data-k="p{i}">{p}</text>')
    flds += f'<div style="display:grid;grid-template-columns:1fr 110px;gap:6px"><div>{field(f"n{i}", f"{i + 1}. Nomi", n)}</div><div>{field(f"p{i}", "Narx", p)}</div></div>'
svg4 = f'''<svg id="tpl" xmlns="http://www.w3.org/2000/svg" width="1240" height="1754" viewBox="0 0 1240 1754" {F}>
<rect width="1240" height="1754" data-c="bg" fill="#0b0b0d"/>
<text x="620" y="230" font-size="120" font-weight="900" text-anchor="middle" fill="#fff" data-k="title">NARXLAR</text>
<text x="620" y="310" font-size="40" letter-spacing="8" text-anchor="middle" data-c="accent" fill="#d4a24c" data-k="sub">USTA BARBERSHOP</text>
<rect x="520" y="350" width="200" height="6" rx="3" data-c="accent" fill="#d4a24c"/>
<text x="1100" y="470" font-size="30" text-anchor="end" fill="#9ca3af" data-k="cur">so'm</text>
{items}
<text x="620" y="1620" font-size="34" text-anchor="middle" fill="#9ca3af" data-k="foot">📞 +998 90 123 45 67  ·  Har kuni 10:00–21:00</text>
</svg>'''
make("dizayn-narxlar", "Narxlar ro'yxati / menyu shabloni (A4)", svg4,
     field("title", "Sarlavha", "NARXLAR") + field("sub", "Nomi", "USTA BARBERSHOP") + field("cur", "Valyuta", "so'm") + flds +
     field("foot", "Pastki qator", "📞 +998 90 123 45 67  ·  Har kuni 10:00–21:00") +
     colors([("bg", "Fon", "#0b0b0d"), ("accent", "Asosiy rang", "#d4a24c")]),
     620, "A4", "narxlar.png", 1, '<button class="alt" onclick="window.print()">🖨 PDF / chop etish</button>')

# ---------------------------------------------------------------- D5 Stories (1080x1920) e'lon
svg5 = f'''<svg id="tpl" xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920" {F}>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" data-c="g1" stop-color="#7c3aed" data-attr="stop-color"/><stop offset="1" data-c="g2" stop-color="#ec4899" data-attr="stop-color"/></linearGradient></defs>
<rect width="1080" height="1920" fill="url(#g)"/>
<circle cx="980" cy="260" r="260" fill="#fff" opacity=".08"/><circle cx="80" cy="1600" r="340" fill="#fff" opacity=".07"/>
<rect x="90" y="250" width="300" height="80" rx="40" fill="#fff" opacity=".2"/>
<text x="240" y="305" font-size="38" font-weight="800" fill="#fff" text-anchor="middle" data-k="tag">YANGILIK</text>
<text x="90" y="560" font-size="130" font-weight="900" fill="#fff" data-k="t1">Yangi</text>
<text x="90" y="700" font-size="130" font-weight="900" fill="#fff" data-k="t2">kurs</text>
<text x="90" y="840" font-size="130" font-weight="900" fill="#fff" data-k="t3">ochildi!</text>
<text x="90" y="980" font-size="50" fill="#fff" opacity=".9" data-k="d1">Grafik dizayn: 3 oyda kasb</text>
<text x="90" y="1050" font-size="50" fill="#fff" opacity=".9" data-k="d2">Birinchi dars bepul</text>
<rect x="90" y="1500" width="900" height="150" rx="75" fill="#fff"/>
<text x="540" y="1597" font-size="54" font-weight="800" text-anchor="middle" data-c="g1" fill="#7c3aed" data-k="cta">Yozilish uchun bosing</text>
<text x="540" y="1760" font-size="40" fill="#fff" opacity=".85" text-anchor="middle" data-k="brand">@bilim_plus</text>
</svg>'''
make("dizayn-stories", "Instagram/Telegram stories e'lon shabloni (1080×1920)", svg5,
     field("tag", "Belgi", "YANGILIK") + field("t1", "Sarlavha 1", "Yangi") + field("t2", "Sarlavha 2", "kurs") + field("t3", "Sarlavha 3", "ochildi!") +
     field("d1", "Izoh 1", "Grafik dizayn: 3 oyda kasb") + field("d2", "Izoh 2", "Birinchi dars bepul") + field("cta", "Tugma matni", "Yozilish uchun bosing") +
     field("brand", "Sahifa", "@bilim_plus") + colors([("g1", "Gradient 1", "#7c3aed"), ("g2", "Gradient 2", "#ec4899")]),
     420, "1080px 1920px", "stories.png", 1)

RD = '''
# {title}

Brauzerda ochiladigan tayyor shablon: matn va ranglarni o'zgartirasiz, bir tugma bilan tayyor faylni yuklab olasiz. Dastur o'rnatish va internet kerak emas.

## Ishlatish
1. `index.html` ni oching (kompyuter yoki telefon brauzerida).
2. Chap tomondagi maydonlarga o'z matningizni yozing, ranglarni tanlang. O'ng tomonda darhol ko'rinadi.
3. **⬇ PNG yuklab olish** tugmasini bosing.{extra}
4. Yanada erkin tahrirlash uchun **SVG** ni yuklab, Figma, Canva yoki bepul Inkscape'da oching.

💡 Emoji (📞 ✉) o'rniga oddiy matn ham yozsa bo'ladi.
'''
for slug, title, extra in [
    ("dizayn-instagram-aksiya", "Instagram aksiya posti shabloni", ""),
    ("dizayn-vizitka", "Vizitka shabloni (90×50 mm)", "\n   Chop etish uchun **🖨 PDF / chop etish** → «PDF sifatida saqlash». Bosmaxonaga PDF yoki PNG ni bering."),
    ("dizayn-sertifikat", "Sertifikat / diplom shabloni (A4)", "\n   Ko'p o'quvchi uchun: ismni almashtirib, har biri uchun PNG yoki PDF saqlang."),
    ("dizayn-narxlar", "Narxlar ro'yxati / menyu shabloni (A4)", "\n   Devorga osish uchun **🖨 PDF / chop etish** orqali A4 chop eting."),
    ("dizayn-stories", "Stories e'lon shabloni (1080×1920)", ""),
]:
    w(f"{slug}/README.md", RD.format(title=title, extra=extra))
print("ok design")
