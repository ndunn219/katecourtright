# Squarespace source capture — November 7, 2026

Reference for [issue #1](https://github.com/ndunn219/katecourtright/issues/1). The capture used public GET requests only; the live website was not modified. Source responses were captured around 18:03 UTC. Each response has its own timestamp in `responses.json`.

## Status

- [x] URL/content inventory, including items requiring a scope decision.
- [x] Reproducible source and asset capture with original URLs and SHA-256 hashes.
- [x] Desktop and representative mobile screenshot evidence saved.
- [x] Representative references accepted; exhaustive capture checklist retired (November 7, 2026).
- [x] Font requirements and missing-source findings documented.

**Issue #1 is complete with the representative reference set accepted by the user on November 7, 2026.** On resumption, native Chrome worked despite the browser connector remaining unavailable. Thirty screenshots are now saved, with sixteen individually inspected: desktop coverage of all eight requested pages, representative mobile coverage of home/About/Contact, and mobile menu behavior. See the [capture notes](screenshots/README.md) for the accepted capture scope, metadata, visual limitations, and checks carried into later work.

## Captured material

| Material | Count |
| --- | ---: |
| Discovered page URLs, including query-based archives | 37 |
| Successful HTML responses | 36 |
| Existing broken page links | 1 |
| Blog posts | 14 |
| Category archives | 4 |
| Author-filter pages | 2 |
| Images from content and the sitemap | 38 |
| Additional CSS image dependencies | 29 |
| Stylesheets | 7 |
| Template script | 1 |
| EPUB downloads | 2 |
| Distinct external links inventoried (not checked) | 104 |

The captured responses total 29,626,182 bytes (about 28.3 MiB), plus the derived inventories and documentation. All 77 asset requests succeeded. The single failed page is `/schedule-appointment-hatch`, an existing HTTP 404 linked by the sample property pages.

## Files

| File/directory | Purpose |
| --- | --- |
| [INVENTORY.md](INVENTORY.md) | Every URL, proposed disposition, post metadata, form locations, links to saved HTML |
| [ASSETS.md](ASSETS.md) | Browseable asset list with local and source links |
| [DESIGN.md](DESIGN.md) | Source-derived typography, layout, responsive behavior, and image geometry |
| [FONTS.md](FONTS.md) | Font families, licensing sources, and an independent setup plan |
| [DECISIONS.md](DECISIONS.md) | Scope decisions and migration traps |
| [screenshots/README.md](screenshots/README.md) | Outstanding visual capture plan |
| `pages/`, `styles/`, `scripts/`, `images/`, `downloads/`, `metadata/` | Unmodified source response bytes |
| `pages.json` | Extracted page metadata, intro/main text, links, image geometry, form blocks, template settings |
| `assets.json` | Source-to-local asset manifest, final URLs, hashes, sizes, and referring pages |
| `responses.json` | All attempted HTTP requests and their results |
| `external-links.json` | Retailer, social, and article links, with referring pages |
| `css-dependencies.json`, `script-dependencies.json` | Runtime dependency inventory; font binaries and global platform JS are reference-only |
| `summary.json` | Machine-readable capture totals and failures |
| `verification.json` | Offline integrity/coverage verification result |

## Reproduction and limits

Run the commands in the [repository README](../../../README.md). The script starts from the sitemap and homepage, follows same-site content links and supported Musings filters, downloads linked `/s/` files, and records external links without crawling other sites. Four concurrent requests and a 200-page bound keep the crawl limited. It captures CSS image dependencies and the template bundle but does not copy the full Squarespace application or Adobe font binaries.

Raw HTML/CSS remain unchanged and retain their live dependencies. This archive is an implementation reference, **not an offline mirror or deployable website**. `main_text` covers the `<main>` element; `intro_text` separately preserves the Musings introduction outside `<main>`. The full HTML remains authoritative for markup, ordering, and content.

Images were requested from the unresized CDN URLs; these are the public delivery assets, not an export of the Squarespace editor's master uploads. The CDN returned **WebP data for all 38 content images**, including URLs ending in `.jpg` or `.png`. Raw filenames retain the source naming, while `content_type` and the bytes record the real format. Use the proper file extension/content type when copying these into the future site.

No assets are missing from the captured asset list. Font licensing/setup and the remaining detailed browser checks are outstanding inputs; representative screenshots are now available. External purchase/social links were inventoried, not validated. Pages omitted from both the public sitemap and discovered links cannot be guaranteed to be covered.

