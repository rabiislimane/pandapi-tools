// Browser checks for the outcome pages (outcome_pages.py) plus the home page and guides hub.
// Run from tools-site/: node test/outcome-pages.js   (serves the folder itself on a free port)
// Checks at 1280 px and 390 px: 0 console errors, no horizontal scroll, all relative links and images resolve,
// JSON-LD parses, one H1, setup button points at a published Apify task, sample table present.
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const ROOT = path.join(__dirname, '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.ico': 'image/x-icon', '.json': 'application/json' };
const SHOTS = process.env.SHOTS_DIR || path.join(os.tmpdir(), 'pandapi-outcome-shots');
fs.mkdirSync(SHOTS, { recursive: true });
const PAGES = ['competitor-price-monitoring/', 'government-tender-alerts/', 'see-competitors-google-ads/', 'domain-ssl-expiry-alerts/', 'app-review-alerts/', 'hiring-alerts/', 'website-technology-lookup/', '', 'guides/'];

let failures = 0;
function check(cond, msg) { if (cond) console.log('  ok  ' + msg); else { failures++; console.log('  FAIL ' + msg); } }

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0].split('#')[0]);
  if (p.endsWith('/')) p += 'index.html';
  const file = path.join(ROOT, p);
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('not found'); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise((r) => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch();
  for (const width of [1280, 390]) {
    for (const rel of PAGES) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await ctx.newPage();
      const errors = [];
      page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
      page.on('pageerror', (e) => errors.push(String(e)));
      // Block external requests so the check is about our page only.
      await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, (route) => route.abort());
      console.log(`${rel || '(home)'} @ ${width}px`);
      const resp = await page.goto(base + rel, { waitUntil: 'load' });
      check(resp.status() === 200, 'loads');
      const info = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        h1: document.querySelectorAll('h1').length,
        ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map((s) => { try { JSON.parse(s.textContent); return true; } catch { return false; } }),
        links: [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href')).filter((h) => !/^(https?:|mailto:|#)/.test(h)),
        imgs: [...document.querySelectorAll('img')].map((i) => i.getAttribute('src')),
        setup: [...document.querySelectorAll('a.btn')].map((a) => a.href).filter((h) => h.includes('create-task-from-example')),
        sampleRows: document.querySelectorAll('.prose table.cmp tbody tr').length,
        title: document.title,
      }));
      check(info.overflow <= 0, `no horizontal scroll (${info.overflow}px)`);
      check(info.h1 === 1, 'one H1');
      check(info.ld.every(Boolean), `JSON-LD parses (${info.ld.length})`);
      for (const h of [...new Set([...info.links, ...info.imgs])]) {
        const u = new URL(h, base + rel).href;
        const r = await page.request.get(u);
        if (r.status() !== 200) check(false, `link ${h} -> ${r.status()}`);
      }
      check(true, `${info.links.length} relative links, ${info.imgs.length} images checked`);
      if (rel.endsWith('/') && rel !== 'guides/') {
        check(info.setup.length >= 2 && info.setup.every((h) => /create-task-from-example\/[A-Za-z0-9]{17}$/.test(h)), 'setup buttons point at a published task');
        check(info.sampleRows >= 2, `sample and price tables present (${info.sampleRows} rows)`);
      }
      check(errors.length === 0, `0 console errors ${errors.join(' | ')}`);
      await page.screenshot({ path: path.join(SHOTS, `${(rel || 'home').replace(/\/$/, '').replace('/', '_')}-${width}.png`), fullPage: true });
      await ctx.close();
    }
  }
  await browser.close();
  server.close();
  console.log(failures ? `${failures} FAILED` : 'all passed', '· screenshots in', SHOTS);
  process.exit(failures ? 1 : 0);
})();
