#!/usr/bin/env python3
"""Read-only, resumable archive of katecourtright.com using Python 3 and curl.

Raw responses stay unchanged. Manifests record provenance, hashes, links, image
geometry, and source metadata. This is reference material, not a deployable site.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import parse_qsl, quote, urlencode, urljoin, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

ORIGIN = "https://katecourtright.com"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
IGNORED_TEXT = {"script", "style", "svg", "noscript"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def normalize(value, base=ORIGIN, image=False):
    value = unescape(value).strip()
    u = urlsplit(urljoin(base, value))
    if u.scheme not in {"http", "https"}:
        return None
    host = u.netloc.lower()
    if host in {"www.katecourtright.com", "katecourtright.com"}:
        host = "katecourtright.com"
    query = parse_qsl(u.query, keep_blank_values=True)
    if image:
        query = [(k, v) for k, v in query if k != "format"]
    return urlunsplit(("https" if host == "katecourtright.com" else u.scheme,
                       host, quote(u.path or "/", safe="/%:@+!$&'()*,-._~="),
                       urlencode(sorted(query)), ""))


class Node:
    def __init__(self, tag="root", attrs=None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), []

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def text(self):
        if self.tag in IGNORED_TEXT:
            return ""
        return " ".join(filter(None, (c.text() if isinstance(c, Node) else c.strip()
                                      for c in self.children)))


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def extract(html, url):
    doc = Document(html)
    nodes = list(doc.root.walk())
    main = next((n for n in nodes if n.tag == "main"), doc.root)
    metadata, links, images, styles, scripts, forms = {}, [], [], [], [], []
    form_blocks = []
    for n in nodes:
        a = n.attrs
        if n.tag == "meta":
            metadata[a.get("property") or a.get("name") or a.get("http-equiv", "unknown")] = a.get("content", "")
        if n.tag == "a" and a.get("href"):
            links.append({"href": a["href"], "url": normalize(a["href"], url), "text": n.text(), "class": a.get("class", "")})
        if n.tag == "link" and a.get("href"):
            rel = a.get("rel", "")
            if rel == "canonical":
                metadata["canonical"] = normalize(a["href"], url)
            if rel == "stylesheet":
                styles.append(normalize(a["href"], url))
        if n.tag == "script" and a.get("src"):
            scripts.append(normalize(a["src"], url))
        if n.tag == "form":
            forms.append({"id": a.get("id"), "class": a.get("class"), "action": a.get("action"), "method": a.get("method")})
        if set(a.get("class", "").split()) & {"sqs-block-form", "sqs-block-newsletter"}:
            form_blocks.append({"id": a.get("id"), "class": a.get("class"), "text": n.text()})
        if n.tag == "img":
            source = a.get("data-src") or a.get("src")
            if source and not source.startswith("data:"):
                images.append({"url": normalize(source, url, image=True), "source": source,
                               "alt": a.get("alt", ""), "dimensions": a.get("data-image-dimensions"),
                               "focal_point": a.get("data-image-focal-point"), "srcset": a.get("srcset"),
                               "class": a.get("class", ""), "style": a.get("style", "")})
        for bg in re.findall(r"url\(['\"]?([^)'\"]+)", a.get("style", "")):
            if not bg.startswith("data:"):
                images.append({"url": normalize(bg, url, image=True), "source": bg, "kind": "inline-background"})
    for key in ["og:image", "twitter:image"]:
        if metadata.get(key):
            images.append({"url": normalize(metadata[key], url, image=True), "source": metadata[key], "kind": key})
    # Squarespace gallery records can exist in data attributes or inline JSON.
    for m in re.finditer(r'"(?:assetUrl|imageUrl)"\s*:\s*"([^"\n]+)"', unescape(html)):
        value = m.group(1).replace("\\/", "/")
        if value.startswith(("http", "//")):
            images.append({"url": normalize(value, url, image=True), "source": value, "kind": "embedded-image-record"})
    context = {}
    marker = "Static.SQUARESPACE_CONTEXT = "
    if marker in html:
        try:
            context = json.JSONDecoder().raw_decode(html.split(marker, 1)[1])[0]
        except ValueError:
            pass
    article = next((n for n in nodes if n.tag == "article" and "BlogItem" in n.attrs.get("class", "").split()), None)
    article_nodes = list(article.walk()) if article else []
    article_meta = next((n for n in article_nodes if "BlogItem-meta" in n.attrs.get("class", "").split()), None)
    meta_nodes = list(article_meta.walk()) if article_meta else []
    post = None
    if article:
        date = next((n for n in meta_nodes if n.tag == "time"), None)
        author = next((n for n in meta_nodes if n.tag == "a" and "author=" in n.attrs.get("href", "")), None)
        categories = [n.text() for n in meta_nodes if n.tag == "a" and "/category/" in n.attrs.get("href", "")]
        post = {"date": date.attrs.get("datetime") if date else None,
                "displayed_date": date.text() if date else None,
                "author": author.text() if author else None,
                "author_url": normalize(author.attrs["href"], url) if author else None,
                "categories": categories}
    return {
        "title": next((n.text() for n in nodes if n.tag == "title"), ""),
        "metadata": metadata,
        "headings": [{"level": n.tag, "text": n.text()} for n in main.walk() if re.fullmatch(r"h[1-6]", n.tag)],
        "main_text": main.text(),
        "intro_text": "\n\n".join(n.text() for n in nodes if n.tag == "section" and "Intro" in n.attrs.get("class", "").split()),
        "dates": [{"datetime": n.attrs.get("datetime"), "text": n.text()} for n in main.walk() if n.tag == "time"],
        "links": links, "images": images, "stylesheets": sorted(set(styles)), "scripts": sorted(set(scripts)), "forms": forms,
        "form_blocks": form_blocks, "post": post,
        "collection": context.get("collection"), "item": context.get("item"),
        "template_id": context.get("templateId"), "tweaks": context.get("tweakJSON", {}),
        "body_classes": next((n.attrs.get("class", "") for n in nodes if n.tag == "body"), ""),
        "controllers": sorted({n.attrs["data-controller"] for n in nodes if "data-controller" in n.attrs}),
    }


def filename(url, kind):
    u = urlsplit(url)
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", unescape(u.path.rsplit("/", 1)[-1])).strip("-.") or "home"
    stem = stem[:90]
    digest = hashlib.sha256(url.encode()).hexdigest()[:12]
    if kind == "pages":
        stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", u.path.strip("/")).strip("-.")[:125] or "home"
        return f"{kind}/{stem}--{digest}.html"
    if kind == "styles" and not stem.endswith(".css"):
        stem += ".css"
    return f"{kind}/{digest}--{stem}"


class Capture:
    def __init__(self, root, refresh, offline):
        self.root, self.refresh, self.offline = root, refresh, offline
        self.cache = root / "responses.json"
        self.responses = json.loads(self.cache.read_text()) if self.cache.exists() else {}

    def fetch(self, url, kind):
        old = self.responses.get(url)
        if self.offline:
            if not old or (old.get("ok") and not (self.root / old["local_path"]).is_file()):
                raise RuntimeError(f"Missing cached response for {url}; run a network capture first.")
            return old
        if old and old.get("ok") and not self.refresh and (self.root / old["local_path"]).is_file():
            return old
        local = filename(url, kind)
        path = self.root / local
        path.parent.mkdir(parents=True, exist_ok=True)
        # Only public GET requests. curl validates TLS, follows redirects, and
        # reports HTTP errors rather than saving them as successful assets.
        proc = subprocess.run([
            "curl", "--location", "--silent", "--show-error", "--fail",
            "--retry", "2", "--max-time", "60", "--connect-timeout", "15",
            "--proto", "=https,http", "--proto-redir", "=https,http",
            "--output", str(path), "--write-out", "%{http_code}\n%{url_effective}\n%{content_type}", url,
        ], text=True, capture_output=True)
        parts = proc.stdout.split("\n")
        ok = proc.returncode == 0 and path.exists()
        record = {"source_url": url, "local_path": local if ok else None, "captured_at": now(),
                  "status": int(parts[0]) if parts and parts[0].isdigit() else None,
                  "final_url": parts[1] if len(parts) > 1 else None,
                  "content_type": parts[2] if len(parts) > 2 else None, "ok": ok}
        if ok:
            data = path.read_bytes()
            record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        else:
            record["error"] = proc.stderr.strip()
        return record

    def batch(self, jobs):
        with ThreadPoolExecutor(max_workers=4) as pool:
            records = list(pool.map(lambda pair: self.fetch(*pair), jobs))
        for record in records:
            self.responses[record["source_url"]] = record
        dump(self.cache, self.responses)
        return records


def page_kind(url):
    u = urlsplit(url)
    p = u.path
    if re.match(r"/musings/\d{4}/", p):
        return "blog-post", "preserve"
    if p.startswith("/musings/category/"):
        return "category-archive", "preserve"
    if p == "/musings" and u.query:
        return "blog-filter", "preserve-behavior"
    if p == "/listing-02-hatch":
        return "book-excerpt-legacy-path", "preserve-content; decide-destination"
    if "hatch" in p:
        return "template-leftover", "decision-required"
    if p == "/newsletter":
        return "signup-page", "retire-signup; decide-old-url"
    if p == "/arc":
        return "arc-signup", "decision-required"
    if p == "/contact":
        return "contact", "preserve-content; remove-form"
    if p == "/search":
        return "search", "replace-behavior"
    return "page", "preserve"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reference/squarespace/2026-11-07"))
    parser.add_argument("--refresh", action="store_true", help="Re-fetch existing responses (use a new output directory for a new snapshot).")
    parser.add_argument("--offline", action="store_true", help="Rebuild inventories from saved responses without network access.")
    args = parser.parse_args()
    if args.refresh and args.offline:
        parser.error("--refresh and --offline cannot be combined")
    cap = Capture(args.output, args.refresh, args.offline)
    sitemap_url = ORIGIN + "/sitemap.xml"
    sitemap = cap.batch([(sitemap_url, "metadata"), (ORIGIN + "/robots.txt", "metadata")])[0]
    if not sitemap["ok"]:
        raise SystemExit("Could not capture sitemap; see responses.json")
    xml = ET.fromstring((args.output / sitemap["local_path"]).read_bytes())
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "i": "http://www.google.com/schemas/sitemap-image/1.1"}
    sitemap_urls = {normalize(n.text) for n in xml.findall("s:url/s:loc", ns)}
    seed_urls = sitemap_urls | {ORIGIN + "/"}
    sitemap_images = {normalize(n.text, image=True) for n in xml.findall("s:url/i:image/i:loc", ns)}
    pending, pages, seen = set(seed_urls), {}, set()
    while pending:
        batch = sorted(pending - seen)
        if not batch:
            break
        if len(seen) + len(batch) > 200:
            raise SystemExit("Stopped at 200-page crawl bound; inspect discovered links.")
        seen.update(batch)
        records = cap.batch([(url, "pages") for url in batch])
        pending = set()
        for record in records:
            url = record["source_url"]
            kind, disposition = page_kind(url)
            page = {**record, "kind": kind, "disposition": disposition, "in_sitemap": url in sitemap_urls}
            if record["ok"] and "html" in record["content_type"]:
                page.update(extract((args.output / record["local_path"]).read_text(errors="replace"), url))
                for link in page["links"]:
                    target = link["url"]
                    if not target:
                        continue
                    u = urlsplit(target)
                    if u.netloc != "katecourtright.com" or u.path.startswith(("/s/", "/api/", "/config/")):
                        continue
                    if Path(u.path).suffix.lower() in {".pdf", ".epub", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp3", ".mobi"}:
                        continue
                    query = dict(parse_qsl(u.query))
                    if query and not (u.path == "/musings" and set(query) <= {"author", "offset", "category", "tag"}):
                        continue
                    pending.add(target)
            pages[url] = page
        dump(args.output / "pages.json", sorted(pages.values(), key=lambda p: p["source_url"]))
        print(f"Captured {len(pages)} pages; {len(pending - seen)} discovered pages remain", flush=True)

    assets = {}
    def add(url, kind, page, occurrence=None):
        if not url:
            return
        entry = assets.setdefault(url, {"kind": kind, "referenced_by": [], "occurrences": []})
        if page not in entry["referenced_by"]:
            entry["referenced_by"].append(page)
        if occurrence and occurrence not in entry["occurrences"]:
            entry["occurrences"].append(occurrence)

    for url in sorted(sitemap_images):
        add(url, "images", sitemap_url)
    for url, page in pages.items():
        for img in page.get("images", []):
            add(img["url"], "images", url, img)
        for css in page.get("stylesheets", []):
            add(css, "styles", url)
        for script in page.get("scripts", []):
            if "/static/ta/" in script and script.endswith("site-bundle.js"):
                add(script, "scripts", url)
        for link in page.get("links", []):
            target = link["url"]
            if not target:
                continue
            u = urlsplit(target)
            if u.netloc == "katecourtright.com" and (u.path.startswith("/s/") or Path(u.path).suffix.lower() in {".epub", ".pdf", ".mobi", ".zip", ".mp3"}):
                add(target, "downloads", url)
    print(f"Capturing {len(assets)} images, styles, downloads, and template script", flush=True)
    cap.batch([(u, a["kind"]) for u, a in sorted(assets.items())])
    # Inventory CSS dependencies. Archive raster/SVG backgrounds, but do not
    # download licensed font binaries or the platform's entire JS dependency tree.
    css_dependencies = []
    extra = []
    for url, entry in list(assets.items()):
        rec = cap.responses[url]
        if entry["kind"] != "styles" or not rec["ok"]:
            continue
        css = (args.output / rec["local_path"]).read_text(errors="replace")
        for value in sorted(set(re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", css))):
            if value.startswith("data:"):
                continue
            target = normalize(value, url)
            if not target:
                continue
            suffix = Path(urlsplit(target).path).suffix.lower()
            is_image = suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}
            css_dependencies.append({"stylesheet": url, "url": target, "action": "archive-image" if is_image else "reference-only"})
            if is_image:
                if target not in assets:
                    extra.append((target, "images"))
                add(target, "images", url)
    if extra:
        cap.batch(extra)
    manifest = [{**cap.responses[url], **entry} for url, entry in sorted(assets.items())]
    dump(args.output / "assets.json", manifest)
    dump(args.output / "css-dependencies.json", css_dependencies)
    scripts = sorted({s for p in pages.values() for s in p.get("scripts", [])})
    dump(args.output / "script-dependencies.json", [{"url": s, "archived": s in assets} for s in scripts])
    external_links = {}
    for page in pages.values():
        for link in page.get("links", []):
            target = link["url"]
            if target and urlsplit(target).netloc != "katecourtright.com":
                external_links.setdefault(target, set()).add(page["source_url"])
    dump(args.output / "external-links.json", [{"url": u, "referenced_by": sorted(refs), "checked": False} for u, refs in sorted(external_links.items())])
    summary = {"origin": ORIGIN, "generated_at": now(), "page_count": len(pages),
               "blog_post_count": sum(p["kind"] == "blog-post" for p in pages.values()),
               "asset_count": len(manifest), "bytes": sum(r.get("bytes", 0) for r in cap.responses.values()),
               "failures": [r for r in cap.responses.values() if not r["ok"]],
               "notes": ["Raw HTML/CSS are unmodified reference captures, not runtime site files.",
                         "Image format resize parameters are removed to request the original CDN asset.",
                         "Fonts and global platform JS are inventoried, not downloaded.",
                         "Re-runs reuse successful responses; use a new output directory for a new snapshot."]}
    dump(args.output / "summary.json", summary)
    write_inventory(args.output, pages, manifest)
    print(json.dumps(summary, indent=2), flush=True)


def write_inventory(root, pages, assets):
    def cell(text):
        return str(text or "—").replace("|", "\\|").replace("\n", " ")

    lines = ["# URL and content inventory", "", "Generated by `scripts/capture_squarespace.py` from saved public responses.", "",
             "Disposition is a migration recommendation, not a deletion or publication action. Raw captures preserve every successful response, including pages proposed for retirement.", "",
             "| URL | Kind | HTTP | Disposition | Saved HTML |", "| --- | --- | --- | --- | --- |"]
    for url, p in sorted(pages.items()):
        local = f"[HTML]({p['local_path']})" if p["local_path"] else "Missing at source"
        path = url.removeprefix(ORIGIN)
        lines.append(f"| [{cell(path)}]({url}) | {p['kind']} | {p['status']} | {p['disposition']} | {local} |")
    lines += ["", "## Blog posts", "", "Keep the displayed publication date separately from the URL date; they often differ. Category assignments below come from each post's metadata, not adjacent-post links.", "",
              "| Post | Displayed date | Author | Categories |", "| --- | --- | --- | --- |"]
    for p in sorted((p for p in pages.values() if p["kind"] == "blog-post"), key=lambda p: (p.get("post") or {}).get("date") or "", reverse=True):
        meta = p.get("post") or {}
        title = (p.get("item") or {}).get("title") or p.get("title")
        lines.append(f"| [{cell(title)}]({p['source_url']}) | {cell(meta.get('displayed_date'))} | {cell(meta.get('author'))} | {cell(', '.join(meta.get('categories', [])))} |")
    lines += ["", "## Form and signup locations", "", "These are source blocks, including forms mounted by Squarespace JavaScript. Raw captures intentionally retain them; removal belongs to issue #4.", "",
              "| Page | Block types |", "| --- | --- |"]
    for p in sorted(pages.values(), key=lambda p: p["source_url"]):
        blocks = p.get("form_blocks", [])
        if blocks:
            kinds = ["contact form" if "sqs-block-form" in b["class"].split() else "newsletter signup" for b in blocks]
            lines.append(f"| [{p['source_url'].removeprefix(ORIGIN)}]({p['source_url']}) | {', '.join(kinds)} |")
    (root / "INVENTORY.md").write_text("\n".join(lines) + "\n")

    lines = ["# Asset inventory", "", "`assets.json` contains full source/final URLs, SHA-256 hashes, byte sizes, referring pages, and image dimensions/focal points where present in the HTML.", "",
             "Image assets are the original CDN endpoints with resize parameters removed. No font binaries are archived. Many CSS images and sample-listing images will not be needed by the replacement site.", "",
             "| Kind | Local file | Bytes | Source | References |", "| --- | --- | ---: | --- | ---: |"]
    for a in sorted(assets, key=lambda a: (a["kind"], a["source_url"])):
        label = Path(a["local_path"]).name if a["local_path"] else "Missing"
        local = f"[{label}]({a['local_path']})" if a["local_path"] else label
        lines.append(f"| {a['kind']} | {local} | {a.get('bytes', 0)} | [source]({a['source_url']}) | {len(a['referenced_by'])} |")
    (root / "ASSETS.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
