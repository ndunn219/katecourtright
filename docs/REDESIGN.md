# Redesign decisions and changes

The November 2026 redesign (tracking issue #17) replaces the Squarespace-parity layout with the design canvas at <https://claude.ai/artifact/1YXR6qKXa53DZo98aNpWRh>. This file records the content and URL decisions made while implementing it, so later reviewers can tell intended changes from regressions. Verification results are in [LAYOUT-VERIFICATION.md](LAYOUT-VERIFICATION.md).

## Books page and retailer links (#11)

- `src/_data/books.json` is structured data: `slug`, `title`, `subtitle`, `cover`, optional `banner`, `summary` and `featured`, and `formats` (`label` plus `stores` of `name`, `url`, optional `shortName`). It contains no HTML. `partials/book.njk` renders format groups and cards. The home page reads the same data.
- All 25 retailer links are kept. The 7 Amazon links were reduced to their canonical product path (`…/dp/<ASIN>`), dropping `/ref=` search-tracking segments and query strings. Every other URL is unchanged, including the Audible link.
- **Amazon affiliate tag (default decision applied):** the It's Up to You, New York link contained `tag=individualbookpagesite-20` and `_bbid=66494394`. Both were removed, leaving `https://www.amazon.com/dp/B09XQJ4FQL`. If Kate confirms the tag is her own Amazon Associates ID, restore it and add the disclosure "As an Amazon Associate I earn from qualifying purchases" plus a privacy-policy line about Amazon cookies. `scripts/check_site.py` currently rejects any `tag=` parameter, so it would need updating too.
- "Available at:" / "Available for download at:" labels became format headings (E-book, Paperback, Audiobook). Compact cards show "B&N" as an `<abbr>` for Barnes & Noble. Each chip carries visually hidden context (for example "Amazon: Pinkie e-book") so links are distinguishable out of context. Retailer links open in the same tab.
- `scripts/check_migration.py` compares Amazon links by product path, and checks this route's restructured copy word by word rather than as contiguous text.

## Home page (#9)

- `/` and `/welcome/` share `layouts/home.njk` and `content/welcome.njk`. The hero is a fixed-height photo with a dark scrim, an H1 tagline and two buttons. The parallax effect, the "Scroll" indicator and their JavaScript were removed. `home-background.webp` is no longer used.
- The welcome copy is unchanged but uses an italic H2 and a lede paragraph instead of `<h2>` blocks. "Follow me on Bookbub & Goodreads, too!" became the buttons "Follow on BookBub" and "Follow on Goodreads", which are recorded as an approved copy replacement in `scripts/check_migration.py`.
- The Latest book section reads the featured book from `books.json`. The From the Musings cards are the three newest posts from `collections.posts`, so they update automatically.
- At phone width, the hero scrim is stronger than in the artboard because the taller text block otherwise sat over bright sky.

## About Kate (#10)

- `/about-late/` is now its own template (in `src/about.njk`) instead of the `split-page` variant, which was removed. The bio is unchanged but split into a lede and two paragraphs.
- The new facts row (Writes / Lives / First story, a `<dl>`) only restates the bio. "Bookbub" is now capitalized "BookBub", matching the service. Both changes are recorded as an approved replacement in `check_migration.py`.
- The Keep reading section links to Books, Works in Progress and Musings.
