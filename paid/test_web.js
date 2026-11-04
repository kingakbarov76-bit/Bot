// Playwright tests for the web projects (C6, C7, C10) + preview screenshots
const { chromium } = require('playwright');
const B = '/home/claude/bot/paid/src/';
const IMG = '/home/claude/bot/paid/img/';
(async () => {
  const b = await chromium.launch();
  const errs = [];
  const page = async (vp) => { const p = await b.newPage({ viewport: vp || { width: 1280, height: 800 } }); p.on('pageerror', e => errs.push(e.message)); return p; };

  // C7 expense tracker
  let p = await page({ width: 900, height: 1000 });
  await p.goto('file://' + B + 'xarajat-hisobchi/index.html');
  for (const [a, c, n] of [[45000, 'Oziq-ovqat', 'bozor'], [12000, 'Transport', 'taksi'], [150000, 'Kommunal', 'svet'], [30000, 'Oziq-ovqat', 'non']]) {
    await p.fill('#amount', String(a)); await p.selectOption('#cat', c); await p.fill('#note', n); await p.click('#add');
  }
  const total = await p.textContent('#tMonth');
  if (!total.includes('237 000')) throw new Error('C7 total ' + total);
  await p.click('.del >> nth=0');
  const cnt = await p.textContent('#tCount'); if (cnt !== '3') throw new Error('C7 delete ' + cnt);
  await p.reload(); if ((await p.textContent('#tCount')) !== '3') throw new Error('C7 persist');
  await p.screenshot({ path: IMG + 'code_xarajat.jpg', quality: 82, type: 'jpeg' });
  console.log('C7 OK', total);

  // C10 quiz
  p = await page({ width: 900, height: 900 });
  await p.goto('file://' + B + 'test-yaratuvchi/index.html');
  await p.screenshot({ path: IMG + 'code_test.jpg', quality: 82, type: 'jpeg' });
  await p.uncheck('#shuffle'); await p.fill('#mins', '0'); await p.click('#start');
  await p.click('.opt >> text=Toshkent'); await p.waitForTimeout(800);
  await p.click('.opt >> text=25'); await p.waitForTimeout(800);
  await p.click('.opt >> text=Python'); await p.waitForTimeout(900);
  const sc = await p.textContent('#score'); if (sc !== '2 / 3') throw new Error('C10 score ' + sc);
  console.log('C10 OK', sc);

  // C6 form (UI validation only; network endpoint is a placeholder)
  p = await page({ width: 900, height: 900 });
  await p.goto('file://' + B + 'forma-telegramga/index.html');
  await p.click('#btn'); const m1 = await p.textContent('#msg'); if (!m1.includes("to'g'ri")) throw new Error('C6 validation');
  await p.route(u => u.hostname.endsWith('workers.dev'), r => r.fulfill({ status: 200, body: 'ok', headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': 'content-type', 'access-control-allow-methods': 'POST, OPTIONS' } }));
  await p.fill('#name', 'Ali'); await p.fill('#phone', '+998901234567'); await p.click('#btn');
  await p.waitForTimeout(500); const m2 = await p.textContent('#msg'); if (!m2.includes('Rahmat')) throw new Error('C6 send ' + m2);
  await p.screenshot({ path: IMG + 'code_forma.jpg', quality: 82, type: 'jpeg' });
  console.log('C6 OK');

  if (errs.length) throw new Error('JS errors: ' + errs.join(' | '));
  await b.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
