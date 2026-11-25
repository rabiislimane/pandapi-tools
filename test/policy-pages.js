// Checks for the policy pages (policy_pages.py) and the policy links in every page's footer.
// Run from tools-site/ after a build with SITE_URL set: node test/policy-pages.js
// 1) Static: every built page has the 6 footer policy links, each resolves to a file; every page keeps its canonical tag.
// 2) Browser at 1280 and 390 px on the 6 policy pages + home + one tool + one guide: 200, one H1, no horizontal
//    scroll, 0 console errors, every relative link and image resolves. 3) privacy.html sends visitors to privacy/.
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.ico': 'image/x-icon', '.json': 'application/json', '.webp': 'image/webp' };
const POLICIES = ['privacy/', 'terms/', 'refunds/', 'cookies/', 'report-emails/', 'contact/'];
const PAGES = [...POLICIES, '', 'html-to-markdown/', 'firecrawl-alternative/'];

let failures = 0;
function check(cond, msg) { if (cond) console.log('  ok  ' + msg); else { failures++; console.log('  FAIL ' + msg); } }

// 1) static footer check over every built page
function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['node_modules', 'vendor', 'test', '__pycache__'].includes(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out); else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}
const files = walk(ROOT).filter((f) => !f.endsWith(`${path.sep}privacy.html`));
let footerOk = 0;
for (const f of files) {
  const s = fs.readFileSync(f, 'utf8');
  const nav = (s.match(/<nav class="footer-policies"[^>]*>(.*?)<\/nav>/) || [])[1] || '';
  const hrefs = [...nav.matchAll(/href="([^"]+)"/g)].map((m) => m[1]);
  const resolved = hrefs.every((h) => fs.existsSync(path.join(path.dirname(f), h, 'index.html')));
  const canon = /<link rel="canonical" href="https:\/\/rabiislimane\.github\.io\/pandapi-tools\//.test(s);
  if (hrefs.length === 6 && resolved && canon) footerOk++;
  else check(false, `${path.relative(ROOT, f)}: ${hrefs.length} footer links, resolve=${resolved}, canonical=${canon}`);
}
check(footerOk === files.length, `${footerOk}/${files.length} pages have the 6 policy links and a canonical tag`);
const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
check(POLICIES.every((p) => sitemap.includes(`/pandapi-tools/${p}</loc>`)), 'sitemap lists the 6 policy pages');

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
      await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, (route) => route.abort());
      console.log(`${rel || '(home)'} @ ${width}px`);
      const resp = await page.goto(base + rel, { waitUntil: 'load' });
      check(resp.status() === 200, 'loads');
      const info = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        h1: document.querySelectorAll('h1').length,
        css: getComputedStyle(document.querySelector('.site-footer')).borderTopStyle,
        links: [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href')).filter((h) => !/^(https?:|mailto:|#)/.test(h)),
        imgs: [...document.querySelectorAll('img')].map((i) => i.getAttribute('src')),
      }));
      check(info.overflow <= 0, `no horizontal scroll (${info.overflow}px)`);
      check(info.h1 === 1, 'one H1');
      check(info.css === 'solid', 'site stylesheet applied');
      for (const h of [...new Set([...info.links, ...info.imgs])]) {
        const r = await page.request.get(new URL(h, base + rel).href);
        if (r.status() !== 200) check(false, `link ${h} -> ${r.status()}`);
      }
      check(true, `${info.links.length} relative links, ${info.imgs.length} images checked`);
      check(errors.length === 0, `0 console errors ${errors.join(' | ')}`);
      await ctx.close();
    }
  }
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(base + 'privacy.html');
  await page.waitForURL(/\/privacy\/$/, { timeout: 5000 }).catch(() => {});
  check(page.url().endsWith('/privacy/'), `privacy.html redirects to privacy/ (${page.url()})`);
  await browser.close();
  server.close();
  console.log(failures ? `${failures} FAILED` : 'all passed');
  process.exit(failures ? 1 : 0);
})();
