import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import vm from 'node:vm';
import { search } from '../src/assets/js/search-core.js';
import { searchDocument } from './search-index.mjs';

const prefix = process.env.SITE_PATH_PREFIX || '/';
const documents = JSON.parse(readFileSync('_site/search-index.json', 'utf8'));
assert.equal(documents.length, 30);
assert.equal(new Set(documents.map(doc => doc.url)).size, 30);
for (const doc of documents) {
  assert.ok(doc.title && doc.text);
  assert.ok(doc.url.startsWith(prefix));
  assert.ok(existsSync(`_site/${decodeURIComponent(doc.url.slice(prefix.length))}index.html`), doc.url);
  assert.ok(!doc.text.includes('Designed & Managed by'));
}
assert.equal(documents.filter(doc => /\/musings\/\d{4}\//.test(doc.url)).length, 14);
assert.ok(!documents.some(doc => /\/(welcome|newsletter|search)\/$/.test(doc.url)));
assert.match(search(documents, 'ANNA quindlen')[0].url, /meeting-anna-quindlen/);
assert.match(search(documents, 'creative path avoiding burnout')[0].url, /the-creative-path-to-avoiding-burnout/);
assert.ok(search(documents, 'Adirondacks').some(doc => doc.url.endsWith('/listing-02-hatch/')), 'Search full bodies, not just titles');
for (const query of ['', '   ', '!!', 'zzzznonexistent', '<script>alert(1)</script>']) {
  assert.equal(search(documents, query).length, 0, query);
}
assert.equal(search([{ title: 'Café & Stories', text: 'A café.', url: '/' }], 'cafe')[0].title, 'Café & Stories');
assert.equal(searchDocument('<header>ignore</header><main><h1>A &amp; B</h1><p>café <em>stories</em></p><script>ignore</script><nav>ignore</nav></main><footer>ignore</footer>').text, 'A & B café stories');

// Small event/DOM doubles execute the shipped handlers. They do not emulate
// browser layout, native details activation, touch input, or accessibility APIs.
class Element {
  constructor() { this.events = {}; this.attrs = {}; this.children = []; this.dataset = {}; this.inert = false; this.style = { setProperty: (key, value) => { this.attrs[key] = value; } }; }
  addEventListener(type, listener) { (this.events[type] ||= []).push(listener); }
  dispatch(type, props = {}) {
    const event = { target: this, preventDefault() { this.prevented = true; }, ...props };
    for (const listener of this.events[type] || []) listener(event);
    return event;
  }
  setAttribute(key, value) { this.attrs[key] = value; }
  removeAttribute(key) { delete this.attrs[key]; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  set innerHTML(_) { throw new Error('Rendering must not use innerHTML'); }
}
const flush = () => new Promise(resolve => setImmediate(resolve));

// Exercise search URL state, empty/no-result states, safe rendering, fetch
// failures and retry, and a stale response arriving after the query is cleared.
const form = new Element();
const input = new Element();
const status = new Element();
const results = new Element();
const searchWindow = new Element();
const location = { href: `https://preview.example${prefix}search/?q=Anna+Quindlen`, search: '?q=Anna+Quindlen' };
let fetchCount = 0;
let failFetch = false;
let releaseFetch;
const searchContext = vm.createContext({
  search, URL, URLSearchParams, location,
  document: {
    querySelector: selector => ({ '.search-form': form, '#search-query': input, '#search-status': status, '#search-results': results })[selector],
    createElement: () => new Element(),
  },
  window: searchWindow,
  history: { pushState: (_state, _unused, url) => { location.href = url.href; location.search = url.search; } },
  fetch: async url => {
    assert.equal(url.href, `https://preview.example${prefix}search-index.json`);
    fetchCount++;
    if (releaseFetch) await new Promise(resolve => { releaseFetch = resolve; });
    if (failFetch) throw new Error('Offline');
    return { ok: true, json: async () => documents };
  },
});
const searchCode = readFileSync('_site/assets/js/search.js', 'utf8')
  .replace(/^import .*\n/, '')
  .replaceAll('import.meta.url', JSON.stringify(`https://preview.example${prefix}assets/js/search.js`));
vm.runInContext(searchCode, searchContext);
await flush();
assert.equal(input.value, 'Anna Quindlen');
assert.match(status.textContent, /results? for/);
assert.match(results.children[0].children[0].children[0].href, /meeting-anna-quindlen/);
input.value = 'zzzznonexistent';
assert.ok(form.dispatch('submit').prevented);
await flush();
assert.match(status.textContent, /No results/);
assert.equal(results.children.length, 0);
assert.equal(new URL(location.href).searchParams.get('q'), input.value);
input.value = '<img src=x onerror=alert(1)>';
form.dispatch('submit');
await flush();
assert.ok(status.textContent.includes(input.value));
input.value = '';
form.dispatch('submit');
assert.match(status.textContent, /Enter a word/);
assert.equal(location.search, '');
assert.equal(fetchCount, 1, 'Reuse the fetched index');
location.search = '?q=longhand';
searchWindow.dispatch('popstate');
await flush();
assert.equal(input.value, 'longhand');
assert.match(results.children[0].children[0].children[0].href, /joys-of-writing-longhand/);
vm.runInContext('index = undefined', searchContext);
failFetch = true;
form.dispatch('submit');
await flush();
assert.match(status.textContent, /temporarily unavailable/);
assert.equal(results.attrs['aria-busy'], undefined);
failFetch = false;
form.dispatch('submit');
await flush();
assert.match(status.textContent, /results? for/);
vm.runInContext('index = undefined', searchContext);
releaseFetch = true;
form.dispatch('submit');
input.value = '';
form.dispatch('submit');
releaseFetch();
await flush();
assert.match(status.textContent, /Enter a word/);
assert.equal(results.children.length, 0);

// Menu state and keyboard behavior, focus restoration, resize and bfcache restore.
const menu = new Element();
menu.open = false;
const toggle = new Element();
const nav = new Element();
const links = Array.from({ length: 6 }, () => new Element());
const background = Array.from({ length: 5 }, () => new Element());
background[0].inert = true; // Preserve an element that was already inert.
const mobile = Object.assign(new Element(), { matches: true });
const win = new Element();
const doc = new Element();
for (const element of [toggle, ...links, ...background]) element.focus = options => { doc.activeElement = element; element.focusOptions = options; };
menu.querySelector = selector => selector === 'summary' ? toggle : nav;
menu.querySelectorAll = () => links;
menu.contains = element => [menu, toggle, nav, ...links].includes(element);
links.forEach(link => { link.closest = () => link; });
doc.querySelector = selector => ({ '.mobile-menu': menu, '.brand': background[1] })[selector];
doc.querySelectorAll = () => background;
win.matchMedia = query => {
  assert.equal(query, '(max-width: 1000px)', 'Menu behavior must match the CSS breakpoint');
  return mobile;
};
vm.runInNewContext(readFileSync('_site/assets/js/site.js', 'utf8'), { document: doc, window: win });
assert.equal(toggle.attrs['aria-expanded'], 'false');
menu.open = true;
menu.dispatch('toggle');
assert.equal(toggle.attrs['aria-expanded'], 'true');
assert.equal(toggle.attrs['aria-label'], 'Close navigation');
assert.ok(background.every(element => element.inert));
assert.equal(doc.activeElement, toggle);
assert.ok(doc.dispatch('keydown', { key: 'Tab', shiftKey: true }).prevented);
assert.equal(doc.activeElement, links.at(-1));
assert.ok(doc.dispatch('keydown', { key: 'Tab', shiftKey: false }).prevented);
assert.equal(doc.activeElement, toggle);
doc.dispatch('focusin', { target: background[1] });
assert.equal(doc.activeElement, toggle);
assert.ok(doc.dispatch('keydown', { key: 'Escape' }).prevented);
assert.equal(menu.open, false);
assert.equal(doc.activeElement, toggle);
assert.ok(background[0].inert);
assert.ok(background.slice(1).every(element => !element.inert));
menu.open = true;
menu.dispatch('toggle');
nav.dispatch('click', { target: links[0] });
assert.equal(menu.open, false);
menu.open = true;
menu.dispatch('toggle');
links[0].focus();
mobile.matches = false;
mobile.dispatch('change');
assert.equal(menu.open, false);
assert.equal(doc.activeElement, background[1]);
mobile.matches = true;
menu.open = true;
menu.dispatch('toggle');
links[0].focus();
win.dispatch('pageshow');
assert.equal(menu.open, false);
assert.equal(toggle.attrs['aria-expanded'], 'false');
assert.equal(doc.activeElement, toggle);
const siteScript = readFileSync('_site/assets/js/site.js', 'utf8');
assert.ok(!/parallax|scroll-indicator|requestAnimationFrame/.test(siteScript), 'Parallax and scroll effects were removed in the redesign');
const css = readFileSync('_site/assets/css/site.css', 'utf8');
assert.match(css, /@media \(prefers-reduced-motion: no-preference\)/, 'Animations must be limited to no-preference');
assert.match(css, /@media \(prefers-reduced-motion: reduce\) \{ html \{ scroll-behavior: auto; \} \}/);
console.log(`PASS interactions ${prefix}: search coverage/ranking, URL and error states, safe rendering, menu focus/state, reduced motion`);
