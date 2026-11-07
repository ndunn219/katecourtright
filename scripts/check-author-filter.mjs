import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

// Exercise the shipped script against links from the actual generated index.
const html = readFileSync('_site/musings/index.html', 'utf8');
const links = [...html.matchAll(/<a href="([^"]+)" data-author-id="([^"]+)"/g)]
  .map(([, href, authorId]) => ({ href: new URL(href, 'https://preview.example').href, dataset: { authorId } }));
assert.equal(links.length, 2);
const code = readFileSync('_site/assets/js/author-filter.js', 'utf8');
for (const [search, expected] of [
  ['', undefined], ['?author=unknown', undefined], ['?author=', undefined],
  ['?author=%22%5D%3Cscript%3E', undefined],
  ...links.flatMap(link => [
    [`?author=${link.dataset.authorId}`, link.href],
    [`?other=value&author=${link.dataset.authorId}`, link.href],
  ]),
]) {
  let redirect;
  vm.runInNewContext(code, {
    URLSearchParams,
    document: { querySelectorAll: selector => { assert.equal(selector, 'a[data-author-id]'); return links; } },
    window: { location: { search, replace: url => { redirect = url; } } },
  });
  assert.equal(redirect, expected, search);
}
console.log('PASS legacy author queries: both authors, hosting prefix, unrelated parameters, empty and unknown IDs');
