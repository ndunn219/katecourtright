# Kate Courtright website migration

Recreate [katecourtright.com](https://katecourtright.com) with Eleventy and GitHub Pages, preserving the existing appearance and content except for the contact form and newsletter signup.

Implementation is tracked in [issues #1–#6](https://github.com/ndunn219/katecourtright/issues). The Eleventy foundation for issue #2 is implemented with shared layouts, custom CSS, and eight representative pages. Full content migration, remaining behavior, and deployment are later steps. The original Squarespace site has not been changed.

## Run and build

Requires Node.js 20 or newer and npm. Python 3.9+ is needed only for verification and the source-capture scripts.

```sh
npm ci
npm run dev
# Open http://localhost:8080/

npm run build          # Custom-domain root; static output in _site/
npm run build:preview  # GitHub repository path /katecourtright/
npm run check          # Build and check both paths; finishes with the root build
```

Build commands clean `_site/` first. Publish **only the contents of `_site/`**, never this checkout or `reference/`. The generated `.nojekyll` marker supports GitHub Pages. No deployment workflow, domain change, or Sites hosting is included in issue #2.

To develop with the repository prefix, use `SITE_PATH_PREFIX=/katecourtright/ npm run dev` and open `http://localhost:8080/katecourtright/`. Other prefixes can be set with `SITE_PATH_PREFIX=/another-path/ npm run build`. Restart the dev server when changing environment variables. `.env.example` documents the variables; `.env` files are not loaded automatically.

The [Eleventy HTML Base plugin](https://www.11ty.dev/docs/plugins/html-base/) applies the configured prefix to links and assets in generated HTML. Write internal URLs as root-relative paths such as `/about-late/` and `/assets/images/about-portrait.webp`; do not add the prefix yourself. CSS asset URLs are relative to the stylesheet, so they work at either host path. External URLs remain external.

## Edit the site

| Location | Purpose |
| --- | --- |
| `src/_includes/layouts/` | Base document, standard page, home, library, blog index, and blog post templates |
| `src/_includes/partials/` | Shared header, footer, book card, and reader links |
| `src/_data/navigation.json` | Desktop and mobile navigation from one list |
| `src/_data/site.js` | Site metadata and owner-controlled font configuration |
| `src/_data/books.json`, `posts.json` | Book cards and representative blog index metadata |
| `src/*.njk`, `src/posts/*.njk` | Page content and front matter |
| `src/_includes/content/welcome.njk` | Shared content for `/` and `/welcome/` |
| `src/assets/css/site.css` | Typography, colors, responsive grids, hero crops, and menu styling |
| `src/assets/css/fonts.css` | Optional licensed self-hosted font declarations |
| `src/assets/images/` | Selected original images, correctly named as WebP |

Add a page as Markdown (`.md`) or Nunjucks (`.njk`) under `src/` with front matter:

```yaml
---
layout: layouts/page.njk
title: Page title
permalink: /page-path/
---
```

The standard layout accepts an optional `image` object (`src`, `alt`, `width`, `height`), `pageClass`, and `hero`/`shortHero` flags. Use the existing About, Contact, and Works pages as examples. For blog posts, set `published` explicitly and keep the legacy `permalink` independent of that date; use `previousPost` and/or `nextPost` objects (`url`, `title`) for adjacent navigation. Updating a shared layout updates every page that uses it.

## Current verification and remaining work

`npm run check` validates the internal link graph, anchor targets, CSS asset references, image metadata/types, source attribution, publication date, representative grids, and archive exclusion under both hosting paths. It does not fetch external destinations or prove visual equivalence.

Freight fonts need an owner-controlled Adobe Fonts project ID or separately licensed webfonts. The build currently warns and uses explicitly documented Georgia/Arial system fallbacks. See [font setup](docs/FONTS.md). Browser verification was skipped at the user's request after browser access failed; [layout verification notes](docs/LAYOUT-VERIFICATION.md) list the reference comparisons and remaining differences.

This is a migration preview with `noindex, nofollow`. The 13 posts not yet migrated, the privacy policy, and retained legacy content links still lead to the live site; see the exact scope in the verification notes. Complete later migration issues and review `src/_data/site.js` before public launch.

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

