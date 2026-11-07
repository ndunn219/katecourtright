# Issue #5: independent interactions and assets

The site uses local JavaScript and ordinary links for its retained visitor interactions. It has no Squarespace runtime, API, asset, icon-font, or signup integration dependency. The original capture remains unchanged and excluded from deployment. This implementation does not publish or alter the live site.

## Behavior decisions

- **Mobile navigation:** native `<details>` remains usable without JavaScript. The enhanced overlay exposes its expanded state and action label, makes background content inert, keeps Tab/Shift+Tab inside the menu, closes on Escape or link activation, and restores focus to its control. Resizing to desktop closes the menu, restores background interaction, and moves focus to the brand if needed. Back/forward cache restoration resets the menu. The control has a 44px touch target. Without JavaScript, navigation opens as a nonmodal dropdown.
- **Anchors and scrolling:** retain home `#intro`/`#reviews`, restore the library `#library` target, and preserve Works' scroll-to-content link and other existing anchors. Native links support deep links, history, and smooth scrolling. Scroll indicators also move keyboard focus to their target. Small local scroll handlers implement hero and homepage-background parallax. CSS supplies the source's 480ms content fade and 170ms navigation transitions. Reduced-motion preferences disable smooth scrolling, entrance/menu animation, and parallax, including preference changes while the page is open.
- **Index controls:** the captured body classes specify `tweak-index-nav-style-none` even though the generic IndexNavigation controller was loaded. No visible index dots are added. No gallery on retained content requires the source's generic gallery machinery.
- **Search:** `/search/?q=` searches a generated JSON index containing 30 retained pages, including all 14 posts and category/author archives. It searches full main content, ranks title/phrase matches first, matches every query term, and ignores case and accents. The index excludes shared navigation/footer/scripts, the homepage alias, 404, search UI, and retired newsletter page. It is regenerated on builds and Eleventy watch rebuilds. Search fetches only the local index, preserves hosting prefixes, supports bookmarkable queries and back/forward navigation, announces status, and handles empty/punctuation-only, no-result, loading, and retryable failure states. Query/results rendering uses text nodes. A page/post directory remains available without JavaScript or on failure. Search is linked in the footer; the original hidden header search stays hidden.
- **Authors:** since the redesign (#13) every post is credited to Kate Courtright. Both legacy `/musings/author/<id>/` archives remain and list all 14 posts; the `?author=` redirect script was removed because `/musings?author=<id>` now shows the same complete list on the index.
- **Sharing:** each post retains Facebook, Twitter, LinkedIn, Reddit, and Tumblr sharing through ordinary links using the canonical production post URL, even in repository previews. These destinations load only when clicked. Labels replace vendor icons. Squarespace likes and share counters are omitted because their storage/count services are unavailable; no fictitious counts or nonfunctional like button are shown. Ordinary page navigation replaces Squarespace AJAX.
- **Assets and credits:** all images, covers, CSS, scripts, backgrounds, and both byte-identical EPUB downloads are repository assets. Existing local WebP images, dimensions, native lazy-loading for below-fold images, and hero priority hints remain in use; no remote lazy-load or responsive-source markup is needed. The optional owner-controlled Adobe Fonts setup from issue #2 remains unchanged. Without it, the site uses the documented system fallbacks. The footer now credits Eleventy and retains the original copyright, privacy link, and Brisbane Creative attribution.
- **Removed forms:** the only permitted form is local GET search with one `q` field. Contact, newsletter, and ARC signup forms and their integrations remain absent. The original source policy still requires the planned issue #6 service review.

## Automated verification

`npm run check` builds and checks both `/katecourtright/` and `/`, finishing with the root build:

- 34 HTML pages and 972 local HTML links/assets, all fragment targets, CSS URLs, image metadata/types, and output isolation.
- All 39 URL decisions, original retained content, dates/authors/categories, archive membership, canonical URLs, sitemap, EPUB hashes and package integrity, and both author-query destinations.
- Local rendering assets only, except the explicitly configured Adobe stylesheet; no Squarespace domains or runtime markers in generated HTML/CSS/JS/JSON. Share destinations use each post's canonical URL.
- Search index coverage and body search, ranking, normalization, empty/no-result queries, safe rendering, query/history state, fetch caching, failure/retry, and stale asynchronous responses.
- Menu expanded state, focus wrapping/restoration, background inert-state restoration, link closure, desktop resize and page restoration, anchor focus, and live reduced-motion changes.
- Signup-removal checks still reject forms outside search and submission handling outside its script, plus signup destinations and integration remnants.

The JavaScript interaction checks execute the shipped scripts against small event/DOM doubles. They verify handler logic, not native browser layout, accessibility announcements, touch behavior, or native `<details>` activation.

## Browser verification limit and launch follow-up

On November 7, 2026, the computer-use inventory again returned **“The browser access host is unavailable.”** No new browser screenshots, console observations, or runtime network-blocking result are claimed. Static asset auditing establishes that no Squarespace resources are referenced; a browser run with those domains blocked remains unverified.

When browser access is restored, check desktop 1440×900 and mobile 390×844 (also a narrow 320px viewport):

1. Open/close the menu with pointer/touch, Enter/Space, and Escape. Tab and Shift+Tab through the overlay; verify focus restoration, background scroll isolation, and resize recovery.
2. Follow homepage/Works scroll indicators and a direct library `#library` link. Verify the crops and effects with reduced motion both enabled and disabled.
3. Search from the footer for “Anna Quindlen,” “Adirondacks,” an empty query, and a nonsense query. Reload a `?q=` URL, use back/forward, and test offline failure and retry. Disable JavaScript and use the browse directory.
4. Block Squarespace asset/runtime domains and inspect home, About, library, Works, Contact, Musings, a post, and Search for broken images, console errors, and unexpected requests. Check both EPUB downloads and both legacy author-query links.
5. Complete licensed-font, external-destination, hosted URL/404, and service-policy review under issue #6 before enabling indexing.
