#!/usr/bin/env python3
"""Compare the migration with the accepted capture, independently of templates."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

from capture_squarespace import Document

CAPTURE = Path('reference/squarespace/2026-11-07')
OUTPUT = Path('_site')
PREFIX = sys.argv[1] if len(sys.argv) > 1 else '/'
ORIGIN = 'https://katecourtright.com'
inventory = json.loads((CAPTURE / 'pages.json').read_text())
mapping = json.loads(Path('docs/url-migration.json').read_text())


def document(path):
    return Document(path.read_text()).root


def generated(route):
    return document(OUTPUT / route.strip('/') / 'index.html')


def has_class(node, name):
    return name in node.attrs.get('class', '').split()


def compact(text):
    return re.sub(r'\s+', '', text)


# Issues #4 and the redesign (#9 onward) authorize only these copy replacements. Keep checking every other
# captured paragraph and link, including the rest of the privacy policy.
WELCOME_FOLLOW = [(
    'Follow me on Bookbub & Goodreads, too!',
    'Follow on BookBub Follow on Goodreads',
)]
COPY_REPLACEMENTS = {
    '/arc/': [(
        'Join my Advanced Reader Copy (ARC)Team! If you would like an Advanced Reader Copy of an upcoming release and can commit to leaving a review when launch time comes around, I would love to add you to my ARC Team.',
        'Advanced Reader Copies (ARC) ARC readers receive an advance copy of an upcoming release and commit to leaving a review at launch.',
    )],
    # Redesign issue #9: the welcome follow line became two buttons.
    '/': WELCOME_FOLLOW,
    '/welcome/': WELCOME_FOLLOW,
    # Redesign issue #10: a facts row (drawn from the bio) precedes the follow
    # line, which gains BookBub's capitalization and two buttons.
    '/about-late/': [(
        'whenever she can. You can follow me on Bookbub & Goodreads, too!',
        'whenever she can. Writes Short & long form love stories Lives New York City First story Cinderella eating spaghetti, age seven'
        ' You can follow me on BookBub & Goodreads, too!',
    )],
    '/privacy-policy/': [(
        'Newsletter Lists All information collected from this site is used only by Kate and is managed by Kate and her web design team. It is not ever sold to a third party or made available for sale. The information collected, such as your email address, is stored in order for Kate to communicate directly with you through newsletters, promotions or special offers. If you do not wish to receive such emails, you may unsubscribe by clicking the link at the bottom of the newsletter.',
        'Contact and Signup Forms This website no longer offers a contact form, newsletter signup, or ARC signup, and does not collect names or email addresses through those forms. If you already receive a newsletter and wish to unsubscribe, use the unsubscribe link in that email.',
    )],
}

# The redesign rebuilt these routes into structured components, so text order
# changed. Every original word must still appear at least as many times as in
# the capture, except the listed retired labels, headings and typo fixes.
# Every original link is still checked below.
RESTRUCTURED = {
    # #11: "Available at:" labels became format headings.
    '/short-stories-novellas/': {'available', 'at', 'for', 'download', '|'},
    # #12: "elecronic" typo fixed; "Cemetery of First Pages for Hello, Honeymoon"
    # became an eyebrow plus heading. Excerpts moved into <details>.
    '/works-in-progress/': {'elecronic', 'for'},
}


def words(text):
    return re.findall(r"[\w’'&|]+", text.lower())


def main(doc):
    return next(n for n in doc.walk() if n.tag == 'main')


def content_blocks(doc):
    return [n for n in main(doc).walk() if has_class(n, 'sqs-html-content')]


def local(route):
    return PREFIX + route.lstrip('/')


def normalized_link(url):
    parts = urlsplit(url)
    if parts.netloc == 'engage.squarespace-mail.com':
        return normalized_link(parse_qs(parts.query)['u'][0])
    # Issue #11 reduces Amazon product links to their canonical /dp/<ASIN> path
    # (dropping /ref= search tracking and query strings, including the
    # unconfirmed affiliate tag). The product identifier must still match.
    if parts.hostname == 'www.amazon.com' and re.search(r'/dp/[A-Z0-9]{10}', parts.path):
        return 'https://www.amazon.com' + re.sub(r'/ref=[^/]*$', '', parts.path)
    # Percent-encoded spaces and literal spaces in existing retailer queries agree.
    return unquote(url)


def post_urls(doc):
    return [n.attrs['href'] for n in main(doc).walk()
            if n.tag == 'a' and re.search(r'/musings/\d{4}/', n.attrs.get('href', ''))]


assert len(mapping) == len({row['source'] for row in mapping}), 'Duplicate URL decisions'
assert {urlsplit(p['source_url']).path + ('?' + urlsplit(p['source_url']).query if urlsplit(p['source_url']).query else '')
        for p in inventory} == {row['source'] for row in mapping if row['status'] != 'download'}, 'Inventory coverage changed'
for row in mapping:
    if row['status'] == 'retired':
        assert row['note'] and row['destination'] is None
        assert not (OUTPUT / row['source'].strip('/')).exists(), row
        assert (OUTPUT / '404.html').exists()
    else:
        path = OUTPUT / row['destination'].lstrip('/')
        assert (path if path.suffix else path / 'index.html').is_file(), row

posts = sorted((p for p in inventory if p['kind'] == 'blog-post'), key=lambda p: p['post']['date'], reverse=True)
assert len(posts) == 14
assert len(list(Path('src/posts').glob('*.njk'))) == 14
expected_posts = [local(urlsplit(p['source_url']).path + '/') for p in posts]
assert post_urls(generated('/musings/')) == expected_posts, 'Index contents/order differ from publication dates'

for p in inventory:
    if not p['ok'] or p['kind'] in ('template-leftover', 'blog-filter', 'signup-page', 'search'):
        continue
    route = urlsplit(p['source_url']).path.rstrip('/') + '/'
    actual = generated(route)
    title = next(n.text() for n in actual.walk() if n.tag == 'title')
    assert title == p['title'], (route, 'document title changed', title, p['title'])
    original = document(CAPTURE / p['local_path'])
    actual_text = compact(main(actual).text())
    replacements = COPY_REPLACEMENTS.get(route, [])
    for old, new in replacements:
        assert compact(old) in compact(main(original).text()), (route, 'copy exception no longer matches capture')
        assert compact(old) not in actual_text, (route, 'retired signup copy returned')
        assert compact(new) in actual_text, (route, 'replacement copy missing')
    for block in content_blocks(original):
        expected_text = compact(block.text())
        for old, new in replacements:
            expected_text = expected_text.replace(compact(old), compact(new))
        if route in RESTRUCTURED:
            available = Counter(words(main(actual).text()))
            missing = {w for w, n in Counter(words(block.text())).items() if available[w] < n} - RESTRUCTURED[route]
            assert not missing, (route, 'restructured copy lost words', missing)
        else:
            assert expected_text in actual_text, (route, 'missing original text', block.text()[:120])
        for n in block.walk():
            if n.tag == 'a' and urlsplit(n.attrs.get('href', '')).netloc:
                expected = normalized_link(n.attrs['href'])
                links = [normalized_link(a.attrs.get('href', '')) for a in main(actual).walk() if a.tag == 'a']
                assert expected in links, (route, 'lost external content link', expected)
    if p['kind'] != 'blog-post':
        continue
    meta = p['post']
    body = next(n for n in actual.walk() if has_class(n, 'post-body'))
    assert compact(body.text()) == compact(' '.join(b.text() for b in content_blocks(original))), (route, 'post body differs')
    assert any(n.tag == 'time' and n.attrs.get('datetime') == meta['date'] and n.text() == meta['displayed_date'] for n in actual.walk()), route
    author_id = parse_qs(urlsplit(meta['author_url']).query)['author'][0]
    assert any(n.tag == 'a' and n.text() == meta['author'] and n.attrs.get('href') == local('/musings/author/' + author_id + '/') for n in actual.walk()), route
    categories = [n.text() for n in main(actual).walk() if n.tag == 'a' and '/category/' in n.attrs.get('href', '')]
    assert categories == meta['categories'], (route, 'categories changed')
    original_rules = sum(has_class(n, 'sqs-block-horizontalrule') for n in main(original).walk())
    assert sum(n.tag == 'hr' for n in body.walk()) == original_rules, (route, 'section dividers lost')

for p in inventory:
    if p['kind'] == 'category-archive':
        route = urlsplit(p['source_url']).path + '/'
        name = unquote(route.split('/')[-2]).replace('+', ' ')
        expected = [local(urlsplit(post['source_url']).path + '/') for post in posts if name in post['post']['categories']]
        assert post_urls(generated(route)) == expected, (route, 'category membership/order')
    elif p['kind'] == 'blog-filter':
        author_id = parse_qs(urlsplit(p['source_url']).query)['author'][0]
        expected = [local(urlsplit(post['source_url']).path + '/') for post in posts if post['post']['author_url'] == p['source_url']]
        assert len(expected) == 7
        assert post_urls(generated('/musings/author/' + author_id + '/')) == expected, 'Author membership/order'

for asset in json.loads((CAPTURE / 'assets.json').read_text()):
    if asset['kind'] != 'downloads':
        continue
    path = OUTPUT / urlsplit(asset['source_url']).path.lstrip('/')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256'], 'EPUB bytes changed'
    with zipfile.ZipFile(path) as book:
        assert book.testzip() is None
        assert book.read('mimetype') == b'application/epub+zip'
        container = ET.fromstring(book.read('META-INF/container.xml'))
        package = container.find('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile').attrib['full-path']
        ET.fromstring(book.read(package))

locations = [n.text for n in ET.parse(OUTPUT / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locations) == len(set(locations)), 'Duplicate sitemap destinations'
expected_sitemap = set()
for file in OUTPUT.rglob('*.html'):
    route = '/' + file.relative_to(OUTPUT).as_posix().removesuffix('index.html')
    doc = document(file)
    canonical = [n.attrs['href'] for n in doc.walk() if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
    assert canonical == [ORIGIN + ('/' if route == '/welcome/' else route)], (route, 'canonical incorrect')
    if route not in ('/welcome/', '/404.html', '/newsletter/', '/search/'):
        expected_sitemap.add(canonical[0])
    for n in doc.walk():
        if n.tag == 'a':
            assert urlsplit(n.attrs.get('href', '')).netloc not in ('katecourtright.com', 'www.katecourtright.com'), (route, 'content link still points to the old site')
assert set(locations) == expected_sitemap, 'Sitemap missing pages or including aliases/retirements'
for url in ['https://www.instagram.com/kate_courtright_/', 'https://www.facebook.com/kate.courtright.nyc']:
    assert any(n.tag == 'a' and n.attrs.get('href') == url for n in generated('/contact/').walk()), 'Social destination lost'

print(f'PASS migration {PREFIX}: {len(mapping)} URL decisions, 14 complete posts, categories/authors, original copy/links/titles, EPUB integrity, canonical URLs and sitemap')
