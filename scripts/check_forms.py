#!/usr/bin/env python3
"""Guard the issue #4 removal across the entire deployable artifact."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit

from capture_squarespace import Document

OUTPUT = Path('_site')
PREFIX = sys.argv[1] if len(sys.argv) > 1 else '/'

# These identify integrations/handlers, not historical mentions of a newsletter.
REMNANTS = re.compile(
    r'sqs-block-(?:form|newsletter)|newsletter-form|newsletter-block|'
    r'form-submission|sqs-form|engage\.squarespace-mail\.com|'
    r'list-manage\.com|mailchimp|static\.klaviyo\.com|'
    r'/api/(?:1/)?(?:form|newsletter)', re.I,
)
SUBMISSION = re.compile(r'\bonsubmit\b|addEventListener\s*\(\s*[\'"]submit[\'"]|\.(?:requestSubmit|submit)\s*\(', re.I)


def read_page(route):
    return Document((OUTPUT / route / 'index.html').read_text()).root


def local(route):
    return PREFIX + route.lstrip('/')


pages = list(OUTPUT.rglob('*.html'))
for file in OUTPUT.rglob('*'):
    if file.suffix not in ('.html', '.js', '.css'):
        continue
    text = file.read_text()
    match = REMNANTS.search(text)
    assert not match, f'{file}: removed signup integration/handler: {match.group()}'
    # Only the independent, local search script may handle form submission.
    if file != OUTPUT / 'assets/js/search.js':
        assert not SUBMISSION.search(text), f'{file}: unexpected submission handler'
    if file.suffix != '.html':
        continue
    route = file.relative_to(OUTPUT).as_posix().removesuffix('index.html')
    base = 'https://build.example' + local(route)
    for node in Document(text).root.walk():
        assert node.tag != 'iframe', f'{file}: embedded runtime'
        if node.tag == 'form':
            assert file == OUTPUT / 'search/index.html', f'{file}: unexpected form'
            assert node.attrs.get('role') == 'search' and node.attrs.get('method') == 'get', 'Unexpected form purpose'
            assert node.attrs.get('action') == local('/search/'), 'Search action must be local'
            fields = [n for n in node.walk() if n.tag in ('input', 'textarea', 'select')]
            assert len(fields) == 1 and fields[0].attrs.get('name') == 'q' and fields[0].attrs.get('type') == 'search', 'Search field changed'
        assert not (node.tag == 'input' and node.attrs.get('type', '').lower() == 'email'), f'{file}: email signup field'
        # Reject local and old-domain links, including extensionless legacy URLs.
        if node.tag == 'a':
            reference = node.attrs.get('href', '')
            href = urlsplit(urljoin(base, reference))
            path = unquote(href.path).rstrip('/')
            # The retirement page still needs its accessible skip-to-content link.
            if not reference.startswith('#') and href.hostname in ('build.example', 'katecourtright.com', 'www.katecourtright.com'):
                assert path not in ('/newsletter', local('/newsletter')), f'{file}: link to retired signup page'
            assert not re.search(r'\b(?:sign\s*up|subscribe|join\s+my.*(?:arc|reader))\b', node.text(), re.I), f'{file}: signup call to action'

for route in ('arc', 'newsletter'):
    page = read_page(route)
    assert 'signup is no longer available' in page.text(), f'{route}: retirement notice missing'
    assert any(n.tag == 'a' and n.attrs.get('href') == local('/musings/') for n in page.walk()), f'{route}: reading alternative missing'

arc = read_page('arc')
assert not re.search(r'\b(?:join my|add you to my)\b', arc.text(), re.I), 'ARC invitation still promises signup'
policy = read_page('privacy-policy').text()
assert 'does not collect names or email addresses through those forms' in policy, 'Policy still implies form collection'
assert 'Newsletter Lists' not in policy, 'Retired newsletter collection policy returned'

contact = read_page('contact')
for url in (
    'https://www.instagram.com/kate_courtright_/',
    'https://www.facebook.com/kate.courtright.nyc',
    'https://www.bookbub.com/authors/kate-courtright',
    'https://www.goodreads.com/author/show/19932939.Kate_Courtright?from_search=true&from_srp=true',
):
    assert any(n.tag == 'a' and n.attrs.get('href') == url for n in contact.walk()), f'Contact social/reader link lost: {url}'

assert 'https://katecourtright.com/newsletter/' not in (OUTPUT / 'sitemap.xml').read_text(), 'Retired signup page in sitemap'
print(f'PASS form removal {PREFIX}: {len(pages)} pages, deployed HTML/JS/CSS, signup links, URL notices and Contact destinations')
