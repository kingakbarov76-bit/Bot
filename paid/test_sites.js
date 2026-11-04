// Test 5 sites: no JS errors, key interactions work, desktop+mobile screenshots -> combined preview
const { chromium } = require('playwright');
const B = '/home/claude/bot/paid/src/';
const IMG = '/home/claude/bot/paid/img/';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ permissions: ['clipboard-read', 'clipboard-write'] });
  const sites = ['sayt-kafe', 'sayt-oquv-markaz', 'sayt-barbershop', 'sayt-portfolio', 'sayt-dokon'];
  for (const s of sites) {
    const errs = [];
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.setViewportSize({ width: 1366, height: 860 });
    await p.goto('file://' + B + s + '/index.html');
    await p.evaluate(() => { window.open = (u) => { window.__opened = u; }; window.prompt = () => null; });
    if (s === 'sayt-kafe' || s === 'sayt-dokon') {
      await p.click('#' + (s === 'sayt-kafe' ? 'dishes' : 'products') + ' button >> nth=0');
      await p.click('#' + (s === 'sayt-kafe' ? 'dishes' : 'products') + ' button >> nth=1');
      await p.click('#' + (s === 'sayt-kafe' ? 'dishes' : 'products') + ' button >> nth=0');
      const c = await p.textContent('#cartCount'); if (c !== '3') throw new Error(s + ' cart ' + c);
      if (s === 'sayt-dokon') { await p.fill('#q', 'kabel'); const n = await p.locator('.prod').count(); if (n !== 2) throw new Error('search ' + n); await p.fill('#q', ''); }
      await p.click('.cartbtn'); await p.fill('#cName', 'Ali'); await p.fill('#cPhone', '+998901234567');
      await p.click('text=WhatsApp orqali buyurtma');
      const u = await p.evaluate(() => window.__opened);
      if (!u || !u.startsWith('https://wa.me/998901234567?text=') || !decodeURIComponent(u).includes('Jami')) throw new Error(s + ' wa ' + u);
      await p.click('.drawer .btn.ghost');
    }
    if (s === 'sayt-barbershop') {
      await p.locator('#bDate').fill(new Date(Date.now() + 86400000).toISOString().slice(0, 10)); await p.locator('#bDate').dispatchEvent('change');
      await p.click('#slots button >> nth=2'); await p.fill('#bName', 'Ali'); await p.fill('#bPhone', '+998901234567');
      await p.click('text=Telegram orqali yozilish'); await p.waitForTimeout(800);
      const u = await p.evaluate(() => window.__opened); if (u !== 'https://t.me/username') throw new Error('barber ' + u);
    }
    if (s === 'sayt-oquv-markaz') {
      const n = await p.locator('.course').count(); if (n !== 6) throw new Error('courses ' + n);
      await p.fill('#rName', 'Ali'); await p.fill('#rPhone', '+998901234567'); await p.click('#reg button'); await p.waitForTimeout(800);
      const u = await p.evaluate(() => window.__opened); if (u !== 'https://t.me/username') throw new Error('oquv ' + u);
    }
    if (s === 'sayt-portfolio') { await p.click('#filters button >> text=Bot'); const n = await p.locator('.work').count(); if (n !== 2) throw new Error('filter ' + n); await p.click('#filters button >> text=Hammasi'); }
    await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(2200);
    await p.screenshot({ path: `/tmp/claude-0/${s}_d.png` });
    const m = await ctx.newPage(); await m.setViewportSize({ width: 390, height: 844 });
    m.on('pageerror', e => errs.push('mobile: ' + e.message));
    await m.goto('file://' + B + s + '/index.html');
    const ov = await m.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    if (ov) errs.push('mobile horizontal overflow');
    await m.screenshot({ path: `/tmp/claude-0/${s}_m.png` });
    if (errs.length) throw new Error(s + ': ' + errs.join(' | '));
    console.log('OK', s);
    await p.close(); await m.close();
  }
  await b.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
