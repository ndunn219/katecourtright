# Kate Courtright website migration

Rebuild [katecourtright.com](https://katecourtright.com) with Eleventy and GitHub Pages: the original content (minus the contact form and newsletter signup) in a new, more readable design.

Implementation is tracked in [issues #1–#6](https://github.com/ndunn219/katecourtright/issues) and the redesign in issues #7–#16 (tracking issue #17). The Eleventy foundation, content migration, signup removal, independent interactions and the redesign are implemented: 34 HTML pages, all 14 Musings posts, category/author archives, retained legacy content, and both EPUB downloads. The original Squarespace site has not been changed. See [migration decisions and verification](docs/CONTENT-MIGRATION.md) for URL handling and remaining work.

## Run and build

Requires Node.js 20 or newer and npm. Python 3.9+ and curl are needed for verification; the deployment-check tests start a temporary localhost HTTP server. Python is also used by the source-capture scripts.

```sh
npm ci
npm run dev
# Open http://localhost:8080/

npm run build          # Root-path preview; static output in _site/
npm run build:preview  # GitHub repository path /katecourtright/
npm run build:production # Explicit custom-domain launch build with indexing
npm run check          # Check preview/production; finishes with root preview
```

Build commands clean `_site/` first. Publish **only the contents of `_site/`**, never this checkout or `reference/`. The generated `.nojekyll` marker supports GitHub Pages.

## GitHub Pages deployment

The [Pages workflow](.github/workflows/pages.yml) installs locked dependencies, checks repository-preview and production builds, and publishes only `_site/`. It deploys pushes to `main` and manual runs on `main`. The repository Actions variable `SITE_ENV` defaults to `preview`; `production` selects the custom-domain root and indexing. The workflow rejects a mismatch between this setting and the configured Pages URL.

Pages is now configured with **GitHub Actions** as its source. The [existing preview](https://ndunn219.github.io/katecourtright/) is live with no custom domain and indexing disabled. The updated deployment passed all 62 HTTP/artifact checks; see [the dated verification record](docs/DEPLOYMENT-VERIFICATION.md) for evidence and remaining launch requirements. The updated workflow passed its [first run](https://github.com/ndunn219/katecourtright/actions/runs/42407667213), including post-deployment verification, and saved its report as an Actions artifact.

See [deployment, updates, and rollback](docs/DEPLOYMENT.md) for repeatable checks, the production switch, DNS preservation, apex/www HTTPS verification, and rollback to Squarespace. Browser QA, the service-policy review, and the domain cutover remain pending. The live domain's DNS is unchanged. No personal access token or deployment secret is needed for the workflow.

To develop with the repository prefix, use `SITE_PATH_PREFIX=/katecourtright/ npm run dev` and open `http://localhost:8080/katecourtright/`. Other prefixes can be set with `SITE_PATH_PREFIX=/another-path/ npm run build`. Restart the dev server when changing environment variables. `.env.example` documents the variables; `.env` files are not loaded automatically.

The [Eleventy HTML Base plugin](https://www.11ty.dev/docs/plugins/html-base/) applies the configured prefix to links and assets in generated HTML. Write internal URLs as root-relative paths such as `/about-late/` and `/assets/images/about-portrait.webp`; do not add the prefix yourself. CSS asset URLs are relative to the stylesheet, so they work at either host path. External URLs remain external.

## Edit the site

| Location | Purpose |
| --- | --- |
| `src/_includes/layouts/` | Base document, standard page (secondary pages), home, library (Books), Musings index and post templates |
| `src/_includes/partials/` | Shared header and mobile menu, footer, book formats/cards, post list, archive links, search form, follow band |
| `src/_data/navigation.json` | Desktop and mobile navigation from one list |
| `src/_data/site.js` | Site metadata and indexing policy |
| `src/assets/fonts/` | Self-hosted Newsreader and Source Sans 3 WOFF2 files with their OFL licenses |
| `src/_data/books.json` | Structured book data: covers, featured flag, formats and retailer links (no HTML) |
| `src/*.njk`, `src/posts/*.njk` | Page content and front matter |
| `src/authors.njk`, `src/categories.njk` | Static archives generated from post metadata |
| `eleventy.config.js` | Post ordering, archive collections, shared filters, and path-prefix configuration |
| `src/assets/js/site.js` | Mobile menu focus management and state |
| `src/assets/js/search*.js`, `scripts/search-index.mjs` | Local search UI, ranking, and build-time full-text index |
| `src/static/s/` | EPUB files at their original download paths |
| `src/sitemap.njk` | Canonical production sitemap |
| `src/_includes/content/welcome.njk` | Shared content for `/` and `/welcome/` |
| `src/assets/css/site.css` | Design tokens, type scale, header/menu/footer, and per-page styles (breakpoints at 1000px and 720px) |
| `src/assets/css/fonts.css` | `@font-face` declarations for the self-hosted fonts |
| `src/assets/images/` | Selected original images as WebP, plus `-w800`/`-w1600` variants from `scripts/resize_images.py` |

Add a page as Markdown (`.md`) or Nunjucks (`.njk`) under `src/` with front matter:

```yaml
---
layout: layouts/page.njk
title: Page title
permalink: /page-path/
---
```

The standard layout (`layouts/page.njk`) is a centred 760px reading column for secondary pages such as ARC, search and 404. Home, About, Books, Works in Progress, Musings, posts, Contact and Privacy have their own templates. `documentTitle` preserves a legacy browser title when it differs from the visible heading; `canonicalPath` overrides the canonical path for aliases such as `/welcome/`. After adding or replacing an image, run `python3 scripts/resize_images.py` (needs Pillow) to make its responsive variants.

Each blog post is an editable HTML body in a `.njk` file with JSON front matter. Set `tags: ["posts"]`, `published` (an explicit `YYYY-MM-DD` string), `author`, `authorId`, `categories` (an array, possibly empty), `title`, and `permalink`. Keep the legacy permalink independent of the displayed publication date. Collections generate the index, category and author archives, and adjacent-post navigation from this single source; there is no separate post index to synchronize. Updating a shared layout updates every page that uses it. See [content editing](docs/CONTENT-MIGRATION.md#editing-and-verification) for a complete example.

## Current verification and remaining work

`npm run check` validates three configurations (repository preview, production root, and root preview), tests the hosted checker against a local HTTP server, and validates the internal link graph, anchor targets, CSS assets, image metadata/types, archive exclusion, and migration fidelity under both hosting paths. It compares original text, links, titles, all post dates/authors/categories, archive membership/order, URL decisions, canonical URLs, sitemap coverage, and EPUB integrity against the accepted capture. It also executes the legacy author-query script against generated archive links and audits generated HTML, JavaScript, and CSS for removed signup integrations and calls to action. See [form-removal decisions and verification](docs/FORM-REMOVAL.md). It also checks the 30-page search index, search ranking and UI states, mobile-menu keyboard/focus handlers, reduced motion, sharing URLs, and external asset exclusion. These handler tests use DOM doubles; they do not replace browser QA. It does not fetch external destinations or prove visual equivalence. The separate `scripts/check_hosted.py` audits deployed files or external links; see the [verification record](docs/DEPLOYMENT-VERIFICATION.md) for actual HTTP results. Site builds do not need the capture archive; the migration checks also read `reference/`.

The site follows the November 2026 redesign (issue #17); see [redesign decisions](docs/REDESIGN.md) and [layout verification](docs/LAYOUT-VERIFICATION.md), which records headless-browser checks at 390–1440px (overflow, tap targets, keyboard, disclosures, reduced motion, network and cookies; repeat with `scripts/browser-qa.cjs`). Fonts are self-hosted: Newsreader (display) and Source Sans 3 (body), both under the SIL Open Font License, with no third-party font host. See [font setup](docs/FONTS.md).

This remains a preview with `noindex, nofollow`. Content links resolve locally, and `/search/?q=` searches retained pages and all 14 posts (also offered as a browse directory without JavaScript). See [independent interactions and verification](docs/INTERACTIONS.md) for navigation, search, sharing and dependency decisions. Before selecting `SITE_ENV=production`, review the deployed preview against the redesign canvas and confirm the new privacy policy with Kate; the domain cutover is tracked in #6.

## Source capture

Start with the [capture report](reference/squarespace/2026-11-07/README.md), then the [page inventory](reference/squarespace/2026-11-07/INVENTORY.md) and [design notes](reference/squarespace/2026-11-07/DESIGN.md).

The archive is reference material, **not the deployable website**. Its raw HTML retains the original forms, external scripts, and Squarespace URLs. Eleventy reads only `src/`; `reference/` is outside both its input/output and the GitHub Pages deployment artifact.

Requires Python 3.9+ and curl; no Python packages are needed.

```sh
# Resume the capture, reusing successful responses.
python3 scripts/capture_squarespace.py

# Regenerate inventories entirely from the captured files.
python3 scripts/capture_squarespace.py --offline

# Verify archive integrity, content coverage, and EPUB files.
python3 scripts/verify_capture.py
```

For a later capture, pass a new dated directory with `--output reference/squarespace/YYYY-MM-DD`. Use `--refresh` only when deliberately replacing responses in an existing snapshot. Failed URLs are retried on an online run; `--offline` reuses their recorded status.

Desktop references for all eight requested pages and representative mobile references are saved. The [capture notes](reference/squarespace/2026-11-07/screenshots/README.md) and manifest record inspected images and capture limitations. The representative set was accepted and issue #1 closed on November 7, 2026; the exhaustive capture checklist is retired.

