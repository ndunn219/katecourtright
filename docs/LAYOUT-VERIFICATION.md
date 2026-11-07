# Issue #2 implementation and verification

This document records the issue #2 baseline. Issue #3 subsequently migrated all posts and retained pages, made content links local, and added category/author archives, downloads, metadata, and legacy URL handling. See [CONTENT-MIGRATION.md](CONTENT-MIGRATION.md) for current content scope and verification; statements below about unmigrated content describe the earlier baseline.

## Scope

Implemented: Eleventy 3.1.8 with a lockfile, clean production builds, shared templates and navigation data, custom responsive CSS, configurable Adobe font embedding, path-prefix support, and developer documentation. Builds read only `src/` and do not depend on the source archive. Selected image copies are mapped in [asset-provenance.json](asset-provenance.json); the archive is unchanged.

Representative routes:

- `/` and `/welcome/`: shared homepage content, bench hero, distinct homepage portrait, muted teal introduction background.
- `/about-late/`: source biography, 7:5 portrait/text layout, stacked mobile layout.
- `/short-stories-novellas/`: featured First Impressions banner, all four remaining covers, two-column book grid, source retailer/audio links.
- `/works-in-progress/`: full-height railway hero and source long-form content, headings, and excerpts.
- `/contact/`: short cropped hero, source invitation and reader links, no contact form.
- `/musings/`: source introduction and 14 dated post cards to exercise the four-column desktop index.
- `/musings/2023/10/27/meeting-anna-quindlen-and-having-enough-bookshelves/`: source post body, bold italic styling, attribution, explicit October 1 publication date, and adjacent-post navigation.

This selection supplies real content for layout work, not completion of issue #3. Thirteen post destinations and the next-post link still point to the live Squarespace site; privacy-policy and any retained legacy links also remain external until migrated. First Impressions downloads, ARC, categories, author archives, and other legacy destinations are outside this implementation. No archive content or scope decisions have been discarded.

## Reference review

Source declarations in [DESIGN.md](../reference/squarespace/2026-11-07/DESIGN.md), original text blocks, and saved images informed the implementation. The saved reference images were visually inspected during this work; **the new site's rendered appearance has not been verified**.

| Reference inspected | Implementation |
| --- | --- |
| Home desktop top/full and mobile top/content | Full viewport bench crop, overlaid desktop branding, separate 70px mobile header, portrait/text introduction; source teal background retained despite the full-page capture artifact |
| About desktop full and mobile full | Wide portrait at left, inset text at right, 34px column gap; mobile portrait above text |
| Library desktop top and middle | Featured banner at 10/12 content width, two-column grid at 8/12 width, uncropped covers and large serif book titles |
| Works desktop top | Full-height railway image and overlay header |
| Contact desktop/mobile full | 214px desktop hero and 96px mobile image below the header; contact invitation retained |
| Musings desktop top, posts, and bottom | Wide beach image, 8/12-width introduction, four-column dated grid; source-hidden author/category metadata remains in data |
| Anna Quindlen desktop top | Uppercase date above 40px heading; bold italic body paragraphs |

Source typography, colors, heading sizes, 640px mobile breakpoint, and horizontal padding steps (150/64/48/36/20px) are encoded in CSS. The book grid stacks on mobile; the blog grid uses four, three, two, and one columns as space decreases. Intermediate column transitions are implementation choices pending rendered comparison.

## Known differences and follow-ups

- **Fonts:** owner-controlled Freight fonts remain unavailable. Georgia/Arial fallbacks change wrapping and page lengths. See [FONTS.md](FONTS.md). Exact font loading/computed typography verification is still pending.
- **Browser QA:** Chrome native access failed; the browser host was unavailable, and alternate browser access was not approved. The user explicitly requested skipping this check. No new-site screenshots, viewport measurements, overflow checks, keyboard interaction checks, or visual match claims are reported.
- **Forms:** newsletter signup and its navigation entry, plus the contact form, are omitted per the migration brief. Footer/page heights consequently differ from the source. Old signup URL decisions remain for issue #4.
- **Behavior:** native `<details>` provides a keyboard-operable mobile navigation disclosure without JavaScript. Its visual overlay is styled, but focus management and browser behavior still need review. Squarespace AJAX, parallax movement, index-navigation controls, sharing widgets, author/category filtering, and search are not reproduced here; behavior work remains for issue #5.
- **Header/footer:** desktop branding wraps; mobile branding stays on one line. The secondary desktop Musings button is shown on hero headers and hidden on white headers, matching the inspected references. Removing Newsletter changes navigation wrapping. Source copyright and design/platform credits are retained; platform credit changes belong to issue #5.
- **Content:** full migration and editorial verification remain for issue #3. The privacy link currently opens the original policy; no revised policy is invented. Pages are marked `noindex, nofollow` until migration and launch review are complete.
- **Assets:** selected original WebP responses are copied with correct extensions, without new responsive derivatives. Image optimization can follow without changing the preserved archive.

## Automated verification

On November 7, 2026:

- A clean `npm ci` from the lockfile succeeded (using the populated npm cache in offline mode).
- `npm run check` built root and `/katecourtright/` variants successfully: eight pages and 146 local HTML links/assets checked in each variant.
- The check also validates fragment targets, CSS asset URLs, image metadata/types, main landmarks, viewport declarations, date/author preservation, all 14 index cards, all five book cards, and archive/dependency exclusion from output.
- Eleventy development mode successfully started at `http://localhost:8080/`; it was stopped after the user skipped browser QA. An HTTP/browser response was not independently confirmed.

These checks verify generated artifacts, not pixel equivalence, external link availability, or font entitlement. Run `npm run check` after further template/content changes. Revisit desktop 1440×900 and mobile 390×844 rendering when browser access and licensed fonts are available.
