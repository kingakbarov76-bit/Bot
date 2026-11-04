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
