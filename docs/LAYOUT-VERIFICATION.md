# Layout verification (redesign)

The site follows the November 2026 redesign canvas (<https://claude.ai/artifact/1YXR6qKXa53DZo98aNpWRh>, tracked in issue #17) rather than the original Squarespace layout. The earlier Squarespace-parity comparison no longer applies and was removed from this file. It is still in the git history, and the reference captures are in `reference/`. Content and URL decisions made during the redesign are in [REDESIGN.md](REDESIGN.md).

## Design system

| Token | Value | Use |
| --- | --- | --- |
| `--ink` | `#3d6870` | Links, eyebrows, buttons |
| `--ink-deep` | `#264950` | Headings, brand, footer background |
| `--text` | `#3c4649` | Body text |
| `--muted` | `#5b6669` | Secondary text and dates |
| `--line` | `#d9e3e4` | Borders and dividers |
| `--sea` | `#edf3f3` | Tinted sections, hover and current-page fills |
| `--sand` | `#f7f4ee` | Musings intro, Cemetery of First Pages |

- **Type:** Newsreader for display text and Source Sans 3 for body text, both self-hosted ([FONTS.md](FONTS.md)). Body is 18px/1.7 (17px at ≤720px). H1 is 58px, H2 42px and H3 25px (H1 38px and H2 32px at ≤720px).
- **Layout:** the content wrapper is 1240px with 56px gutters (20px at ≤720px).
- **Breakpoints:** ≤1000px collapses the menu and narrows grids; ≤720px is the phone layout. Plain media queries are used, not container queries.
- **Components:** buttons are 48px pills. Retailer, share and social chips are 44px pills, slightly taller than the artboard's 40px to meet the 44px target-size rule.

## Contrast (WCAG 2.x, computed November 7, 2026)

| Foreground on background | Ratio | Result |
| --- | --- | --- |
| `--text` on white | 9.70:1 | AA/AAA |
| `--muted` on white / `--sea` / `--sand` | 5.92 / 5.27 / 5.39:1 | AA |
| `--ink` on white / `--sea` / `--sand` | 6.15 / 5.48 / 5.61:1 | AA |
| White on `--ink` (buttons, badges, tags) | 6.15:1 | AA |
| Footer text `#c9d8da` / `#b9cdd0` / headings `#a9c3c6` on `--ink-deep` | 6.66 / 5.91 / 5.26:1 | AA |

The old body color `#7a7d7f` (which failed AA) is gone. White text on the home hero sits on a dark scrim, which is stronger on phones, where the text covers more of the photo.

## Automated checks (November 7, 2026)

`npm run check` passed for the repository preview (`/katecourtright/`), production root and root preview builds. Each build had 34 HTML pages and 1,197 local links/assets, and the run covered:

- **Link graph:** anchors, CSS URLs (including font files), image dimensions/types and `srcset` candidates, one `<main>` per page, and the indexing policy.
- **Migration fidelity:** the 39 URL decisions, all 14 post bodies, dates, categories, archive membership/order, canonical URLs, sitemap and EPUB integrity. Approved redesign copy changes are listed explicitly in `scripts/check_migration.py`.
- **Forms:** only the two local search forms exist; no signup remnants.
- **Search and menu:** search behavior, menu focus/state logic, and the absence of parallax code.
- **Fonts:** no third-party font hosts, every font file present as WOFF2, and the OFL license files deployed.
- **Privacy-policy claims:** no cookie, storage or analytics code, and no inline or non-local scripts.
- **Book data:** structured, with no HTML strings and no affiliate tag.

`python3 scripts/verify_capture.py` still validates the archived capture.

## Browser checks (headless Chromium, November 7, 2026)

`npm run build:preview && node scripts/browser-qa.cjs _site` (Playwright; not part of `npm run check`) passed with exit code 0:

- **Horizontal overflow:** none on any of the 34 pages at 390, 768, 1024 or 1440px wide.
- **Tap targets:** at 390px, every link, button, summary and input outside running text is at least 44px tall. Post items in the Musings lists use the whole row as the target. Inline links in paragraphs and the byline fall under the WCAG 2.5.8 inline exception.
- **Keyboard:** a Tab pass on every page at 390 and 1440px found a visible focus indicator (2px `--ink` outline, 3px offset) at every stop. The skip link is the first stop.
- **Menu and disclosures:** with JavaScript on and off, the mobile menu opens from the keyboard and focus moves into it. It closes with Escape (JS on) or by toggling its summary (JS off). The Cemetery of First Pages and the Musings "Why I write these" disclosures open and close with Enter and Space.
- **Reduced motion:** with `prefers-reduced-motion: reduce`, the content fade is off and scrolling is `auto`. There are no parallax or scroll effects at all.
- **Network and privacy:** visiting every page plus a search query made no request to any other host, set no cookies, and wrote nothing to `localStorage` or `sessionStorage`. Newsreader and Source Sans 3 (roman and italic) loaded from `/assets/fonts/`.
- **Visual review:** full-page screenshots at 390 and 1440px were compared by eye with the artboards for Home, About, Books, Works in Progress, Musings, a post, Contact and Privacy, plus the secondary pages: search, ARC, First Impressions ARC copy, newsletter notice, 404, the legacy Fire Boy listing, and category/author archives.

### Deliberate differences from the artboards

- **Chips:** retailer, share and social chips are 44px tall instead of 40px, for target size.
- **Home hero:** the phone scrim is darker than the artboard's.
- **Works in Progress:** every original paragraph is kept (the artboard shows a subset). The closed-page preview sits inside each `<summary>` so it shows while the page is closed. The "On this page" list has no scroll-tracked current state.
- **Musings:** all of the intro text is kept inside "Why I write these" (the artboard abridges it), and topic chips follow the year list.
- **Privacy and Contact:** the policy has no "draft" badge, and Contact has no email placeholder.

## Performance

- Photos and covers have explicit `width`/`height`. Images below the fold use `loading="lazy"`, and the first image on each page uses `fetchpriority="high"`.
- `scripts/resize_images.py` makes 800px and 1600px WebP variants, which the templates offer through `srcset`/`sizes`. For example, a book cover card now loads about 60–120 KB instead of up to 3.6 MB.
- Only two font files are preloaded: Source Sans 3 Latin roman and Newsreader Latin roman.
- The only JavaScript is the mobile menu enhancement (`site.js`) and the search page module.

## Not verified here

- Real touch devices and Safari/Firefox rendering.
- Screen-reader output.
- External destination availability.
- The deployed GitHub Pages preview, after this branch is merged (see #6).
