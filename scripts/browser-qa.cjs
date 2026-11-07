// Optional browser QA for the redesigned site (not part of `npm run check`).
// Requires Playwright with Chromium (`npm i -D playwright` or a global install).
//   npm run build:preview && node scripts/browser-qa.cjs _site
// Serves the build under /katecourtright/, then at 390/768/1024/1440px checks
// every page for horizontal overflow and (at 390px) tap targets under 44px;
// runs a keyboard Tab pass at 390 and 1440px confirming every stop shows a
// focus ring; operates the mobile menu and <details> disclosures by keyboard
// with and without JavaScript; and checks reduced-motion handling.
// Inline text links are exempt from the target-size check (WCAG 2.5.8).
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.resolve(process.argv[2] || '_site'), prefix = '/katecourtright/';
const server = http.createServer((req, res) => { let p = decodeURIComponent(req.url.split('?')[0]); if (!p.startsWith(prefix)) { res.writeHead(404); return res.end(); } p = path.join(root, p.slice(prefix.length)); if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html'); if (!fs.existsSync(p)) { res.writeHead(404); return res.end(); } res.writeHead(200, {'content-type': {'.html':'text/html','.css':'text/css','.js':'text/javascript','.woff2':'font/woff2','.webp':'image/webp','.json':'application/json'}[path.extname(p)]||'application/octet-stream'}); fs.createReadStream(p).pipe(res); }).listen(0, async () => {
  const base = `http://127.0.0.1:${server.address().port}${prefix}`;
  const files = []; (function walk(d){ for (const f of fs.readdirSync(d)) { const q = path.join(d,f); if (fs.statSync(q).isDirectory()) walk(q); else if (f === 'index.html') files.push(path.relative(root, d)); } })(root);
  files.push('404.html');
  const browser = await chromium.launch();
  const out = { overflow: [], smallTargets: [], noFocusRing: [], keyboard: [], motion: [] };
  for (const width of [390, 768, 1024, 1440]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 } });
    const page = await ctx.newPage();
    for (const f of files) {
      const url = base + (f === '404.html' ? f : f ? f + '/' : '');
      await page.goto(url, { waitUntil: 'load' });
      const r = await page.evaluate(() => {
        const vis = e => { const b = e.getBoundingClientRect(); const s = getComputedStyle(e); return b.width > 0 && b.height > 0 && s.visibility !== 'hidden' && !e.closest('[hidden], details:not([open]) > :not(summary)'); };
        const small = [...document.querySelectorAll('a[href], button, summary, input')].filter(vis).filter(e => {
          if (e.closest('.prose p, .prose li, .post-topics, .post-meta, .excerpt, .page-copy') && getComputedStyle(e).display === 'inline') return false; // inline text links are exempt (WCAG 2.5.8 inline exception)
          if (e.closest('.post-item, .post-card')) { const b = e.closest('.post-item, .post-card').getBoundingClientRect(); return b.height < 44; } const b = e.getBoundingClientRect(); return b.height < 44 && b.height > 0 && !(e.closest('.mobile-menu-panel'));
        }).map(e => `${e.tagName}.${e.className}:"${e.textContent.trim().slice(0, 20)}":${Math.round(e.getBoundingClientRect().height)}`);
        return { overflow: document.documentElement.scrollWidth - innerWidth, small: [...new Set(small)].slice(0, 5) };
      });
      if (r.overflow > 0) out.overflow.push(`${width} ${f}: ${r.overflow}px`);
      if (r.small.length && width === 390) out.smallTargets.push(`${f}: ${r.small.join(' | ')}`);
      if (width === 390 || width === 1440) {
        // Keyboard pass: every Tab stop shows a focus indicator.
        await page.evaluate(() => document.activeElement.blur());
        let stops = 0; const seen = new Set();
        for (let i = 0; i < 80; i++) {
          await page.keyboard.press('Tab');
          const info = await page.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e); const host = e.closest('.post-item, .post-card'); const hs = host && getComputedStyle(host); return { id: e.outerHTML.slice(0, 60), ring: (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || (hs && hs.outlineStyle !== 'none') }; });
          if (!info || seen.has(info.id)) break; seen.add(info.id); stops++;
          if (!info.ring) out.noFocusRing.push(`${width} ${f}: ${info.id}`);
        }
      }
    }
    await ctx.close();
  }
  // Mobile menu and <details> by keyboard, without JS too.
  for (const js of [true, false]) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: js });
    const page = await ctx.newPage();
    await page.goto(base + 'works-in-progress/');
    await page.focus('.mobile-menu summary'); await page.keyboard.press('Enter');
    const open = await page.evaluate(() => document.querySelector('.mobile-menu').open);
    await page.keyboard.press('Tab');
    const inMenu = await page.evaluate(() => !!document.activeElement.closest('.mobile-menu'));
    if (js) await page.keyboard.press('Escape'); else { await page.focus('.mobile-menu summary'); await page.keyboard.press('Enter'); }
    const closed = await page.evaluate(() => !document.querySelector('.mobile-menu').open);
    const d = page.locator('.first-page summary').first(); await d.focus(); await page.keyboard.press('Enter');
    const detailsOpen = await page.evaluate(() => document.querySelector('.first-page').open);
    await page.keyboard.press(' ');
    const detailsClosed = await page.evaluate(() => !document.querySelector('.first-page').open);
    await page.goto(base + 'musings/'); await page.focus('.read-more summary'); await page.keyboard.press('Enter');
    const readMore = await page.evaluate(() => document.querySelector('.read-more').open);
    out.keyboard.push(`js=${js}: menu opens ${open}, focus moves into menu ${inMenu}, closes ${closed}; first-page opens ${detailsOpen}, closes ${detailsClosed}; Musings disclosure ${readMore}`);
    await ctx.close();
  }
  const ctx = await browser.newContext({ reducedMotion: 'reduce' }); const page = await ctx.newPage();
  await page.goto(base);
  out.motion.push(await page.evaluate(() => ({ mainAnimation: getComputedStyle(document.querySelector('main')).animationName, scroll: getComputedStyle(document.documentElement).scrollBehavior })));
  console.log(JSON.stringify({ pages: files.length, ...out }, null, 1));
  const failed = out.overflow.length || out.smallTargets.length || out.noFocusRing.length
    || out.keyboard.some(line => line.includes('false;') || line.endsWith('false'))
    || out.motion.some(m => m.mainAnimation !== 'none' || m.scroll !== 'auto');
  await browser.close(); server.close();
  process.exitCode = failed ? 1 : 0;
});
