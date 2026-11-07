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

## Works in Progress (#12)

- The page keeps **all** of its text. A word-count comparison of the source before and after the change found only two words missing: the typo "elecronic", now "electronic", and the "for" in the old heading "Cemetery of First Pages for Hello, Honeymoon". That heading became the eyebrow "Hello, Honeymoon" above the heading "Cemetery of First Pages". `check_migration.py` enforces this with word counts.
- The pull quote "A story does need to delight me before I can call it done." repeats a sentence from the text. It is `aria-hidden` so screen readers don't read it twice.
- Each first page and the Shakespeare in the Glen chapter is a native `<details>`. The summary shows the title, a status tag and a chevron. The italic one-line preview (the excerpt's first sentence) sits inside the summary so it shows while the page is closed, and it is hidden when open. The original status "July 2023 Still Breathing" reads "Still breathing · July 2023". The breathing page is open by default and ends with a link to Contact.
- Section headings have `id`s (`hello-honeymoon`, `cemetery-of-first-pages`, `shakespeare-in-the-glen`, plus `hello-friends` on the intro) for the sticky "On this page" list, which is hidden at ≤1000px. No scroll-spy JavaScript was added, so the list has no current-section state.

## Musings index, posts and bylines (#13)

- **Bylines (default decision applied):** all 14 posts now have `author: "Kate Courtright"`. Previously seven were credited to "Kate Dunn" and seven to "Vasheena Brisbane", the web designer's Squarespace account. Each post keeps its legacy `authorId`.
- **Author archive URLs:** both legacy archives, `/musings/author/5c8160afdb7926584fdf6899/` and `/musings/author/536510cee4b043dbe028347e/`, still exist (no URL in `docs/url-migration.json` breaks). Each is titled "Musings by Kate Courtright" and lists all 14 posts. The post byline links to its archive. Because the author list was now redundant, the index's "Browse" links show categories only. `author-filter.js`, which redirected `/musings?author=<id>` to an author archive, was removed: that URL now shows the full index, which is the same list.
- **Index:** the visible H1 is "On creativity, the writing journey, and storytelling". The document title and meta keep the original long title. The intro's `<h2>` blocks became paragraphs: the first is the lede and the other six are in a "Why I write these" `<details>`, with no text removed. The post count and year groups are computed from `collections.posts` (`postsByYear` is also available). The search form submits to `/search/`.
- **Archives:** the category and author pages use the same year-grouped list and topic chips.
- **Posts:** the layout is a 720px column with a back link, eyebrow (the first category, or "Musings"), H1, a "By Kate Courtright · date" meta row, a drop cap, and categories as "Filed under" links. Share links are Facebook, LinkedIn, Reddit and Email (`mailto:`); Twitter and Tumblr were dropped. Newer/Older are `--sea` cards. The duplicate meta line at the bottom was removed.
- In the header, Musings is marked `aria-current="true"` on posts and archives, and `aria-current="page"` on the index.

## Contact (#14)

- Two columns: the lake photo, then the copy (eyebrow, "Contact Me", lede) and four linked tiles with inline stroke icons, ending with "Thank you!". The photo is 320px tall at ≤1000px and 200px at ≤720px.
- **No email address (default decision applied).** The artboard's dashed "Optional: add a direct email link" note was left out. If Kate wants one later, add a fifth tile or a `mailto:` line here, and update the privacy policy.
- "Be sure to follow me on Bookbub & Goodreads, too!" became the BookBub and Goodreads tiles. This is an approved replacement in `check_migration.py`. All four social URLs are unchanged and come from `src/_data/site.js`.
- The `hero` and `shortHero` page-layout options were removed. `layouts/page.njk` is now just the plain content layout used by the secondary pages.
