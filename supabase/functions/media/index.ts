// media: GitHub'dagi media/ papkadagi mp4 fayllarni to'g'ri Content-Type (video/mp4) bilan beradi (Instagram va Telegram uchun).
const BASE = "https://raw.githubusercontent.com/kingakbarov76-bit/bot/main/media/";

Deno.serve(async (req: Request) => {
  const f = new URL(req.url).searchParams.get("f") ?? "";
  if (!/^[A-Za-z0-9_-]{1,60}\.mp4$/.test(f)) return new Response("bad name", { status: 400 });
  const r = await fetch(BASE + f, { headers: { "user-agent": "media-proxy" } });
  if (!r.ok) { await r.body?.cancel(); return new Response("not found", { status: 404 }); }
  const buf = new Uint8Array(await r.arrayBuffer());
  const h = { "content-type": "video/mp4", "content-length": String(buf.length), "accept-ranges": "none", "cache-control": "public, max-age=3600" };
  if (req.method === "HEAD") return new Response(null, { headers: h });
  return new Response(buf, { headers: h });
});
