#!/usr/bin/env python3
"""Compare a deployed site with _site, or audit its external navigation links.

Uses curl for the platform TLS trust store. Network checks are explicit, separate
from offline build checks; JSON reports retain failures for human review.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import quote, urlsplit, urlunsplit


def fetch(url):
    with tempfile.TemporaryDirectory() as directory:
        body = Path(directory) / 'body'
        result = subprocess.run([
            'curl', '--silent', '--show-error', '--location', '--max-redirs', '5',
            '--connect-timeout', '10', '--max-time', '30',
            '--proto', '=http,https', '--proto-redir', '=http,https',
            '--user-agent', 'KateCourtrightMigrationCheck/1.0',
            '--output', str(body), '--write-out', '%{http_code}\n%{url_effective}', url,
        ], capture_output=True, text=True)
        status, _, final_url = result.stdout.partition('\n')
        return {
            'url': url, 'status': int(status or 0), 'final_url': final_url,
            'error': result.stderr.strip(),
            'sha256': sha256(body.read_bytes()).hexdigest() if body.exists() else None,
        }


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href', '')
        if tag == 'a' and urlsplit(href).scheme in ('http', 'https'):
            self.urls.add(href)


def external_targets(output):
    targets = {}
    skipped = set()
    for file in sorted(output.rglob('*.html')):
        links = Links()
        links.feed(file.read_text())
        for href in links.urls:
            url = urlsplit(href)
            # These compose a social post, rather than identify navigable content.
            if (url.hostname, url.path.rstrip('/')) in {
                ('www.facebook.com', '/sharer/sharer.php'), ('twitter.com', '/intent/tweet'),
                ('www.linkedin.com', '/shareArticle'), ('www.reddit.com', '/submit'),
                ('www.tumblr.com', '/share/link'),
            }:
                skipped.add(href)
                continue
            clean = urlunsplit((url.scheme, url.netloc, quote(url.path, safe='/%:@+'), quote(url.query, safe='=&%+/:?@'), ''))
            targets.setdefault(clean, []).append(file.relative_to(output).as_posix())
    return targets, sorted(skipped)


def hosted_targets(output, base):
    targets = []
    for file in sorted(output.rglob('*')):
        if not file.is_file() or file.name.startswith('.'):
            continue
        route = file.relative_to(output).as_posix().removesuffix('index.html')
        targets.append((base + quote(route, safe='/+'), 200, sha256(file.read_bytes()).hexdigest()))
    # Exercise a real missing URL and every intentionally retired legacy route.
    missing = {'__migration-check-missing__/nested/'}
    missing.update(row['source'].lstrip('/') for row in json.loads(Path('docs/url-migration.json').read_text()) if row['status'] == 'retired')
    error_hash = sha256((output / '404.html').read_bytes()).hexdigest()
    targets.extend((base + quote(route, safe='/+'), 404, error_hash) for route in sorted(missing))
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--base-url', help='Deployed base URL, including repository prefix for preview')
    mode.add_argument('--external', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=Path('_site'), help='Matching build or extracted deployment artifact')
    args = parser.parse_args()
    output = args.output_dir
    if not (output / 'index.html').is_file():
        parser.error('Build the matching site configuration first.')
    skipped = []
    if args.external:
        targets, skipped = external_targets(output)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(fetch, sorted(targets)))
        for row in results:
            row['sources'] = targets[row['url']]
            row['ok'] = not row['error'] and 200 <= row['status'] < 300
    else:
        url = urlsplit(args.base_url)
        if url.scheme not in ('http', 'https') or not url.netloc or url.query or url.fragment:
            parser.error('--base-url must be an HTTP(S) base URL without a query or fragment.')
        targets = hosted_targets(output, args.base_url.rstrip('/') + '/')
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(fetch, [target[0] for target in targets]))
        for row, (_, status, digest) in zip(results, targets):
            row['expected_status'] = status
            row['content_matches'] = row['sha256'] == digest
            row['ok'] = not row['error'] and row['status'] == status and row['content_matches'] and row['final_url'] == row['url']
    failures = sum(not row['ok'] for row in results)
    report = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'mode': 'external' if args.external else 'hosted',
        'base_url': args.base_url, 'checked': len(results), 'failures': failures,
        'skipped_share_urls': skipped, 'results': results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f'{len(results)} URLs checked; {failures} failures/review items. Report: {args.report}')
    for row in results:
        if not row['ok']:
            print(f'REVIEW {row["status"]}: {row["url"]} {row["error"]}')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
