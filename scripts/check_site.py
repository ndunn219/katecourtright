#!/usr/bin/env python3
"""Validate the generated link graph and migration boundaries without a browser."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlsplit
import json
import os
import re
import sys

OUTPUT = Path('_site').resolve()
PREFIX = sys.argv[1] if len(sys.argv) > 1 else '/'
ORIGIN = 'https://build.example'


class Page(HTMLParser):
    def __init__(self, file):
        super().__init__(convert_charrefs=True)
        self.file = file
        self.ids = set()
        self.references = []
        self.tags = []
        self.feed(file.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'{self.file}: duplicate id {attrs["id"]}'
            self.ids.add(attrs['id'])
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.references.append(attrs[key])
        if attrs.get('srcset'):
            self.references.extend(item.strip().split()[0] for item in attrs['srcset'].split(','))
        if tag == 'img':
            assert 'alt' in attrs, f'{self.file}: missing image alt'
            assert int(attrs.get('width', 0)) > 0 and int(attrs.get('height', 0)) > 0, f'{self.file}: missing image dimensions'
        assert tag != 'iframe', f'{self.file}: unexpected {tag}'
        if tag == 'form':
            assert self.file in (OUTPUT / 'search/index.html', OUTPUT / 'musings/index.html') and attrs.get('role') == 'search', f'{self.file}: unexpected form'
            assert attrs.get('action') == PREFIX + 'search/' and attrs.get('method') == 'get', 'Search must stay local'
        assert not any(key.startswith('on') for key in attrs), f'{self.file}: inline event handler'
        assert not (tag == 'script' and attrs.get('src', '').startswith('http')), f'{self.file}: unexpected external runtime'
        # Rendering must not depend on Squarespace, a font host, or any other asset host.
        resources = [attrs.get(key, '') for key in ('src', 'poster')]
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'preload', 'icon'):
            resources.append(attrs.get('href', ''))
        if attrs.get('srcset'):
            resources.extend(item.strip().split()[0] for item in attrs['srcset'].split(','))
        for resource in resources:
            host = urlsplit(resource).hostname
            assert not host, f'{self.file}: external asset {resource}'


def resolve_reference(reference, base_url):
    url = urlsplit(urljoin(base_url, reference))
    if url.netloc != 'build.example':
        return None, None
    assert url.path.startswith(PREFIX), f'{base_url}: URL escaped hosting prefix: {reference}'
    relative = unquote(url.path[len(PREFIX):])
    target = (OUTPUT / relative).resolve()
    assert target.is_relative_to(OUTPUT), f'{reference}: path escaped output'
    if target.is_dir():
        target /= 'index.html'
    assert target.is_file(), f'{base_url}: missing local destination {reference} ({target})'
    return target, unquote(url.fragment)


pages = {file: Page(file) for file in OUTPUT.rglob('*.html')}
assert len(pages) >= 8, 'Representative pages missing'
assert (OUTPUT / '.nojekyll').is_file(), 'GitHub Pages marker missing'
for forbidden in ('reference', 'node_modules', 'scripts', 'docs'):
    assert not (OUTPUT / forbidden).exists(), f'{forbidden} leaked into deployment'

count = 0
for file, page in pages.items():
    route = file.relative_to(OUTPUT).as_posix().removesuffix('index.html')
    base = ORIGIN + PREFIX + route
    assert sum(tag == 'main' for tag, _ in page.tags) == 1, f'{file}: expected one main landmark'
    assert any(tag == 'h1' for tag, _ in page.tags), f'{file}: missing heading'
    assert any(tag == 'meta' and attrs.get('name') == 'viewport' for tag, attrs in page.tags), f'{file}: missing viewport'
    private_page = route in ('404.html', 'newsletter/', 'search/')
    robots = ('noindex, follow' if private_page else 'index, follow') if os.environ.get('SITE_ENV') == 'production' else 'noindex, nofollow'
    assert [attrs.get('content') for tag, attrs in page.tags if tag == 'meta' and attrs.get('name') == 'robots'] == [robots], f'{file}: incorrect indexing policy'
    assert any(tag == 'meta' and attrs.get('name') == 'description' and attrs.get('content') for tag, attrs in page.tags), f'{file}: missing description'
    assert any(tag == 'summary' and attrs.get('aria-controls') == 'mobile-navigation' for tag, attrs in page.tags), f'{file}: menu control missing'
    assert 'mobile-navigation' in page.ids, f'{file}: menu target missing'
    if re.match(r'musings/\d{4}/', route):
        # Share URLs carry the page in a query parameter; profile links do not.
        shares = [attrs['href'] for tag, attrs in page.tags if tag == 'a' and urlsplit(attrs.get('href', '')).hostname in ('www.facebook.com', 'twitter.com', 'www.linkedin.com', 'www.reddit.com', 'www.tumblr.com') and urlsplit(attrs['href']).query]
        # Redesign #13: Facebook, LinkedIn, Reddit and Email (Twitter and Tumblr dropped).
        assert len(shares) == 3, f'{file}: sharing controls missing'
        mail = [attrs['href'] for tag, attrs in page.tags if tag == 'a' and attrs.get('href', '').startswith('mailto:')]
        assert len(mail) == 1 and parse_qs(urlsplit(mail[0]).query)['body'] == ['https://katecourtright.com/' + route], f'{file}: email share'
        for share in shares:
            query = parse_qs(urlsplit(share).query)
            assert (query.get('url') or query.get('u')) == ['https://katecourtright.com/' + route], f'{file}: wrong share destination'
    for reference in page.references:
        assert not reference.startswith('javascript:'), f'{file}: unsafe URL'
        target, fragment = resolve_reference(reference, base)
        if target:
            count += 1
            if fragment and target in pages:
                assert fragment in pages[target].ids, f'{file}: missing anchor {reference}'

for file in OUTPUT.rglob('*.css'):
    css = re.sub(r'/\*.*?\*/', '', file.read_text(), flags=re.S)
    base = ORIGIN + PREFIX + file.relative_to(OUTPUT).as_posix()
    for reference in re.findall(r'url\([\s\'"]*([^\)\'"\s]+)', css):
        assert not urlsplit(reference).hostname, f'{file}: external CSS asset {reference}'
        resolve_reference(reference, base)

for file in OUTPUT.rglob('*'):
    if file.suffix in ('.html', '.css', '.js', '.json'):
        assert not re.search(r'(?:squarespace(?:-cdn|-mail)?\.com|sqspcdn\.com|sqs-block-|Static\.SQUARESPACE_CONTEXT)', file.read_text(), re.I), f'{file}: Squarespace dependency returned'
        assert not re.search(r'typekit|googleapis|gstatic|fonts\.bunny|fontawesome', file.read_text(), re.I), f'{file}: third-party font host'

# Self-hosted fonts: every declared face and its license are deployed.
fonts_css = (OUTPUT / 'assets/css/fonts.css').read_text()
for family in ('Newsreader', 'Source Sans 3'):
    assert f"font-family: '{family}'" in fonts_css, f'{family} not declared'
for license_file in ('newsreader/OFL.txt', 'source-sans-3/OFL.txt'):
    assert (OUTPUT / 'assets/fonts' / license_file).is_file(), f'{license_file} missing'
for font in re.findall(r"url\('\.\./fonts/([^']+)'\)", fonts_css):
    assert (OUTPUT / 'assets/fonts' / font).read_bytes()[:4] == b'wOF2', f'{font}: not WOFF2'

post = OUTPUT / 'musings/2023/10/27/meeting-anna-quindlen-and-having-enough-bookshelves/index.html'
assert 'datetime="2023-10-01"' in post.read_text(), 'Publication date was lost or derived from permalink'
assert 'By <a' in post.read_text() and 'Kate Courtright</a>' in post.read_text(), 'Byline missing'
for file in OUTPUT.glob('musings/[0-9]*/**/index.html'):
    assert not re.search(r'Vasheena|Kate Dunn', file.read_text()), f'{file}: legacy byline (redesign #13 credits every post to Kate Courtright)'
index = OUTPUT / 'musings/index.html'
assert sum(tag == 'article' for tag, _ in pages[index].tags) == 14, 'Blog grid must exercise all 14 entries'
library = OUTPUT / 'short-stories-novellas/index.html'
assert sum(tag == 'article' for tag, _ in pages[library].tags) == 5, 'Book grid incomplete'
assert pages[OUTPUT / 'index.html'].ids == pages[OUTPUT / 'welcome/index.html'].ids, 'Homepage alias diverged'

# Correct image file extensions and a complete, reproducible source mapping.
for asset in json.loads(Path('docs/asset-provenance.json').read_text()):
    path = Path(asset['file'])
    assert path.suffix == '.webp' and path.read_bytes()[8:12] == b'WEBP', f'{path}: incorrect image type'

print(f'PASS {PREFIX}: {len(pages)} pages, {count} local links/assets, CSS URLs, anchors, metadata and archive isolation')

# Book data is structured: no HTML strings, and every retailer link is a plain URL.
books = json.loads(Path('src/_data/books.json').read_text())
assert sum(book.get('featured', False) for book in books) == 1, 'Exactly one featured book'
for book in books:
    assert '<' not in json.dumps(book), f'{book["slug"]}: HTML in book data'
    for store in (store for fmt in book['formats'] for store in fmt['stores']):
        assert urlsplit(store['url']).scheme == 'https', store
        assert 'tag=' not in store['url'], f'{store["url"]}: unconfirmed affiliate tag'
