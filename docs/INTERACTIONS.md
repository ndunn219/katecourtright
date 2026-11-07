# Issue #5: independent interactions and assets

The site uses local JavaScript and ordinary links for its retained visitor interactions. It has no Squarespace runtime, API, asset, icon-font, or signup integration dependency. The original capture remains unchanged and excluded from deployment. This implementation does not publish or alter the live site.

## Behavior decisions

- **Mobile navigation:** at ≤1000px a native `<details>` menu remains usable without JavaScript. It opens a full-height panel below the sticky header with large links and a Follow Kate panel. The enhanced version exposes its expanded state and action label, makes the background inert, keeps Tab/Shift+Tab inside the menu, closes on Escape or when a link is activated, and restores focus to its control. Resizing to desktop closes the menu and moves focus to the brand if needed, and restoring the page from the back/forward cache resets the menu. The control is a 44px target. The header is a solid sticky bar (redesign #8) and never overlays a photo.
- **Anchors and scrolling:** the home `#intro`/`#reviews`, library `#library` and other existing anchors are kept, and the Works sections gained ids for its "On this page" list. Native links handle deep links, history and smooth scrolling (with `scroll-padding-top` for the sticky header). The redesign (#9) removed parallax and the scroll indicators along with their JavaScript. CSS supplies a 480ms content fade and 170ms hover transitions. With reduced motion, smooth scrolling and all animation are off.
- **Index controls:** the captured body classes specify `tweak-index-nav-style-none` even though the generic IndexNavigation controller was loaded. No visible index dots are added. No gallery on retained content requires the source's generic gallery machinery.
- **Search:** `/search/?q=` searches a generated JSON index containing 30 retained pages, including all 14 posts and category/author archives. It searches full main content, ranks title/phrase matches first, matches every query term, and ignores case and accents. The index excludes shared navigation/footer/scripts, the homepage alias, 404, search UI, and retired newsletter page. It is regenerated on builds and Eleventy watch rebuilds. Search fetches only the local index, preserves hosting prefixes, supports bookmarkable queries and back/forward navigation, announces status, and handles empty/punctuation-only, no-result, loading, and retryable failure states. Query/results rendering uses text nodes. A page/post directory remains available without JavaScript or on failure. Search is linked in the footer; the original hidden header search stays hidden.
- **Authors:** since the redesign (#13) every post is credited to Kate Courtright. Both legacy `/musings/author/<id>/` archives remain and list all 14 posts; the `?author=` redirect script was removed because `/musings?author=<id>` now shows the same complete list on the index.
- **Sharing:** each post shares to Facebook, LinkedIn, Reddit and Email (`mailto:`) through ordinary links that use the canonical production post URL, even in repository previews. Twitter and Tumblr were dropped in redesign #13. The destinations load only when clicked. Squarespace likes and share counters are omitted.
- **Assets and credits:** all images, covers, fonts, CSS, scripts and both byte-identical EPUB downloads are repository assets. Photos and covers have explicit dimensions, and below-the-fold images lazy-load. Hero and above-the-fold images use `fetchpriority="high"` and have 800/1600px `srcset` variants (from `scripts/resize_images.py`). Fonts are self-hosted (see [FONTS.md](FONTS.md)). The footer has the 2019–2026 copyright plus Privacy Policy and Search links, with no platform or designer credit (redesign #8).
- **Removed forms:** the only forms are the local GET search forms on `/search/` and `/musings/`, each with a single `q` field. Contact, newsletter and ARC signup forms and their integrations remain absent.

## Automated verification

`npm run check` builds and checks both `/katecourtright/` and `/`, finishing with the root build:

- 34 HTML pages and 972 local HTML links/assets, all fragment targets, CSS URLs, image metadata/types, and output isolation.
- All 39 URL decisions, original retained content, dates/authors/categories, archive membership, canonical URLs, sitemap, EPUB hashes and package integrity, and both author-query destinations.
- Local rendering assets only, with no third-party font host; no Squarespace domains or runtime markers in generated HTML/CSS/JS/JSON. Share destinations use each post's canonical URL.
- Search index coverage and body search, ranking, normalization, empty/no-result queries, safe rendering, query/history state, fetch caching, failure/retry, and stale asynchronous responses.
- Menu expanded state, focus wrapping/restoration, background inert-state restoration, link closure, desktop resize and page restoration at the 1000px breakpoint; absence of parallax/scroll code; reduced-motion CSS.
- Signup-removal checks still reject forms outside search and submission handling outside its script, plus signup destinations and integration remnants.

The JavaScript interaction checks execute the shipped scripts against small event/DOM doubles. They verify handler logic, not native browser layout, accessibility announcements, touch behavior, or native `<details>` activation.

## Browser verification

Browser checks for the redesign are recorded in [LAYOUT-VERIFICATION.md](LAYOUT-VERIFICATION.md) and can be repeated with `scripts/browser-qa.cjs`. The remaining manual items are touch input on real devices, screen-reader announcements, and external destination availability.
