const { chromium } = require('playwright');
const fs = require('fs');
const B = '/home/claude/bot/paid/src/';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ acceptDownloads: true, viewport: { width: 1400, height: 900 } });
  for (const s of ['dizayn-instagram-aksiya', 'dizayn-vizitka', 'dizayn-sertifikat', 'dizayn-narxlar', 'dizayn-stories']) {
    const errs = [];
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + B + s + '/index.html');
    const first = p.locator('[data-text]').first(); const k = await first.getAttribute('data-text');
    await first.fill('SINOV MATN');
    const t = await p.locator(`#tpl [data-k="${k}"]`).first().textContent();
    if (t !== 'SINOV MATN') throw new Error(s + ' bind ' + t);
    await p.locator('[data-color]').first().fill('#00aa55');
    const [dl] = await Promise.all([p.waitForEvent('download'), p.click('text=PNG yuklab olish')]);
    const f = '/tmp/claude-0/' + s + '.png'; await dl.saveAs(f);
    const size = fs.statSync(f).size; if (size < 5000) throw new Error(s + ' png small ' + size);
    const [dl2] = await Promise.all([p.waitForEvent('download'), p.click('text=SVG')]);
    await dl2.saveAs('/tmp/claude-0/' + s + '.svg');
    await p.goto('file://' + B + s + '/index.html'); await p.waitForTimeout(300);
    await p.screenshot({ path: '/tmp/claude-0/' + s + '_ui.png' });
    if (errs.length) throw new Error(s + ' ' + errs.join('|'));
    console.log('OK', s, size);
  }
  await b.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
