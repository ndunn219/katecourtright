#!/usr/bin/env python3
"""Validate the generated link graph and migration boundaries without a browser."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import json
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
        assert tag not in ('form', 'iframe'), f'{self.file}: unexpected {tag}'
        assert not any(key.startswith('on') for key in attrs), f'{self.file}: inline event handler'
        assert not (tag == 'script' and attrs.get('src', '').startswith('http')), f'{self.file}: unexpected external runtime'


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
        resolve_reference(reference, base)

post = OUTPUT / 'musings/2023/10/27/meeting-anna-quindlen-and-having-enough-bookshelves/index.html'
assert 'datetime="2023-10-01"' in post.read_text(), 'Publication date was lost or derived from permalink'
assert 'Kate Dunn' in post.read_text(), 'Source attribution missing'
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
