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
    const text = `📩 Yangi ariza\n👤 ${clean(d.name, 60)}\n📞 ${clean(d.phone, 30)}\n🛠 ${clean(d.service, 40)}\n💬 ${clean(d.text, 800)}`;
    const r = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ chat_id: env.CHAT_ID, text }),
    });
    return new Response(r.ok ? "ok" : "telegram error", { status: r.ok ? 200 : 502, headers: cors });
  },
};
