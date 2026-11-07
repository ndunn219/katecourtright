#!/usr/bin/env python3
"""Verify a saved capture offline; report screenshot completeness separately."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import zipfile


def verify_screenshots(root):
    """Validate recorded evidence; never infer visual completeness from hashes."""
    manifest = root / "screenshots/captures.json"
    if not manifest.is_file():
        return {"status": "pending", "recorded": 0, "inspected": 0, "errors": []}
    records = json.loads(manifest.read_text())["screenshots"]
    errors = []
    seen = set()
    for record in records:
        name = record["file"]
        path = (manifest.parent / name).resolve()
        if path.parent != manifest.parent.resolve() or name in seen:
            errors.append(f"Invalid or duplicate screenshot path: {name}")
            continue
        seen.add(name)
        if not path.is_file():
            errors.append(f"Missing screenshot: {name}")
            continue
        data = path.read_bytes()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            errors.append(f"Screenshot size/hash mismatch: {name}")
        if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append(f"Invalid PNG: {name}")
            continue
        width, height = struct.unpack(">II", data[16:24])
        if {"width": width, "height": height} != record["image_pixels"]:
            errors.append(f"Screenshot dimensions differ from metadata: {name}")
        viewport = record["viewport_css"]
        scale = record["device_scale_factor"]
        if width != viewport["width"] * scale:
            errors.append(f"Screenshot width differs from viewport/DPR: {name}")
        if "full" not in record["state"] and height != viewport["height"] * scale:
            errors.append(f"Screenshot height differs from viewport/DPR: {name}")
        for key in ("url", "captured_at", "browser", "page_zoom_percent", "state"):
            if not record.get(key):
                errors.append(f"Missing screenshot metadata {key}: {name}")
    return {"status": "references available; original checklist partial",
            "recorded": len(records), "inspected": sum(r.get("inspected") is True for r in records),
            "evidence_integrity_passed": not errors, "errors": errors,
            "checklist": "screenshots/README.md",
            "note": "Inspection flags record manual review. Hashes and dimensions do not prove loaded fonts, images, or complete visual coverage."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reference/squarespace/2026-11-07"))
    args = parser.parse_args()
    root = args.output.resolve()
    read = lambda name: json.loads((root / name).read_text())
    responses, pages, assets = read("responses.json"), read("pages.json"), read("assets.json")
    errors, known_missing, checked = [], [], 0
    local_paths = set()

    for url, r in responses.items():
        if not r["ok"]:
            if url == "https://katecourtright.com/schedule-appointment-hatch" and r["status"] == 404:
                known_missing.append({"url": url, "status": 404, "note": "Existing sample-listing link is missing at source."})
            else:
                errors.append(f"Unexpected failed request: {url} ({r['status']})")
            continue
        path = (root / r["local_path"]).resolve()
        if root not in path.parents:
            errors.append(f"Path outside archive: {path}")
            continue
        if r["local_path"] in local_paths:
            errors.append(f"Duplicate local path: {r['local_path']}")
        local_paths.add(r["local_path"])
        if not path.is_file():
            errors.append(f"Missing file: {r['local_path']}")
            continue
        data = path.read_bytes()
        if len(data) != r["bytes"] or hashlib.sha256(data).hexdigest() != r["sha256"]:
            errors.append(f"Size/hash mismatch: {r['local_path']}")
        checked += 1

    page_urls = {p["source_url"] for p in pages}
    asset_urls = {a["source_url"] for a in assets}
    sitemap = responses["https://katecourtright.com/sitemap.xml"]
    xml = ET.fromstring((root / sitemap["local_path"]).read_bytes())
    sitemap_urls = {n.text for n in xml.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
    for url in sorted(sitemap_urls - page_urls):
        errors.append(f"Sitemap page absent from inventory: {url}")
    for p in pages:
        if not p["ok"]:
            continue
        if not p.get("title") or "html" not in p["content_type"]:
            errors.append(f"Invalid HTML page: {p['source_url']}")
        if p["kind"] == "blog-post":
            meta = p.get("post") or {}
            if not all(meta.get(k) for k in ["date", "displayed_date", "author", "author_url"]):
                errors.append(f"Incomplete post metadata: {p['source_url']}")
            if len(p.get("main_text", "")) < 100:
                errors.append(f"Post body missing or unexpectedly short: {p['source_url']}")
        for i in p.get("images", []):
            if i["url"] not in asset_urls:
                errors.append(f"Unarchived image on {p['source_url']}: {i['url']}")
        for css in p.get("stylesheets", []):
            if css not in asset_urls:
                errors.append(f"Unarchived stylesheet: {css}")
        for link in p.get("links", []):
            url = link["url"]
            if url and urlsplit(url).netloc == "katecourtright.com" and url not in page_urls | asset_urls:
                errors.append(f"Uninventoried internal link on {p['source_url']}: {url}")
    musings = next(p for p in pages if p["source_url"] == "https://katecourtright.com/musings")
    if len(musings.get("intro_text", "")) < 100:
        errors.append("Musings introduction outside <main> was not extracted.")
    excerpt = next(p for p in pages if p["source_url"] == "https://katecourtright.com/listing-02-hatch")
    if "Fire Boy" not in excerpt.get("main_text", "") or not excerpt["disposition"].startswith("preserve"):
        errors.append("The real Fire Boy excerpt was not preserved in the inventory.")

    epub_checks, image_formats = [], Counter()
    for a in assets:
        if not a["ok"]:
            errors.append(f"Missing asset: {a['source_url']}")
            continue
        data = (root / a["local_path"]).read_bytes()
        if a["kind"] == "downloads" and a["source_url"].endswith(".epub"):
            try:
                with zipfile.ZipFile(root / a["local_path"]) as book:
                    bad = book.testzip()
                    if bad or book.read("mimetype").strip() != b"application/epub+zip" or "META-INF/container.xml" not in book.namelist():
                        errors.append(f"Invalid EPUB: {a['source_url']} (entry: {bad})")
                    else:
                        epub_checks.append({"url": a["source_url"], "entries": len(book.namelist()), "valid": True})
            except (zipfile.BadZipFile, KeyError) as exc:
                errors.append(f"Invalid EPUB: {a['source_url']}: {exc}")
        if a["kind"] == "images":
            mime = a["content_type"].split(";")[0]
            valid = ((mime == "image/webp" and data[:4] == b"RIFF" and data[8:12] == b"WEBP")
                     or (mime == "image/png" and data.startswith(b"\x89PNG\r\n\x1a\n"))
                     or (mime == "image/jpeg" and data.startswith(b"\xff\xd8\xff"))
                     or (mime == "image/gif" and data.startswith((b"GIF87a", b"GIF89a")))
                     or (mime == "image/svg+xml" and b"<svg" in data[:1000]))
            if not valid:
                errors.append(f"Image signature/content type mismatch: {a['local_path']} ({mime})")
            image_formats[mime] += 1

    visual = verify_screenshots(root)
    result = {"verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "archive_checks_passed": not errors, "response_files_verified": checked,
              "pages": len(pages), "successful_pages": sum(p["ok"] for p in pages),
              "blog_posts": sum(p["kind"] == "blog-post" for p in pages),
              "assets": len(assets), "image_formats": dict(image_formats), "epubs": epub_checks,
              "known_missing_at_source": known_missing, "errors": errors,
              "visual_verification": visual,
              "note": "Integrity verification does not establish visual parity or complete issue #1."}
    (root / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not errors and not visual["errors"] else 1)


if __name__ == "__main__":
    main()
