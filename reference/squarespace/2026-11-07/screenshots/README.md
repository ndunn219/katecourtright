# Browser reference captures

Captured **November 7, 2026**, from the live Squarespace site using **Google Chrome 156.0.8078.80**. The browser connector remained unavailable, but native Chrome controls worked. The original source archive was not refreshed and no live content or forms were changed/submitted.

Desktop: **1440 × 900 CSS pixels**. Mobile: **390 × 844 CSS pixels**. Both use **DPR 1, 100% page zoom** in Chrome's Responsive device toolbar. Its fitted preview does not change the exported PNG dimensions. The cookie banner was dismissed before capture. Browser version was read from the installed app's Info.plist.

The saved HTML/CSS and asset inventory are the primary implementation reference. Screenshots supplement them for visible layout, wrapping, crops, and interactive states. The user accepted the representative set and authorized closing issue #1 on November 7, 2026. **The exhaustive capture checklist is retired; no additional screenshots are required to complete the inventory.**

## Coverage

| Page | Desktop | Mobile |
| --- | --- | --- |
| `/` | Top, footer, full | Top, open menu, content, footer, full |
| `/about-late` | Top, full | Full |
| `/short-stories-novellas` | Top, middle, bottom, two full captures with limitations below | Not captured |
| `/works-in-progress` | Top, excerpt, full | Not captured |
| `/musings` | Top, scrolled list views, full | Not captured |
| Anna Quindlen post | Top, full including next-post navigation | Not captured |
| `/contact` | Top, full including original form | Full including original form |
| `/first-impressions` | Top, full including cover | Not captured |

[Capture manifest](captures.json) records all 30 filenames, URLs, UTC capture timestamps (download file modification times), states, browser, viewport, DPR, dimensions, hashes, and individual review flags. Sixteen images were visually inspected; the others are supplemental viewport captures. Integrity checks do not count as visual inspection.

## Observations and limitations

- Mobile menu opens to a white overlay, closes with its X, and navigates successfully to About Kate. The closed menu and normal About layout are recorded. See `home-mobile-menu-open.png` and `about-mobile-full.png`.
- Desktop navigation wraps to two rows. The homepage header scrolls out of view. The mobile header is a centered title with the menu icon to its left. Search and header social icons were not visible in the inspected views.
- Full-page capture is unreliable for this site's parallax/lazy-image effects. Home introduction backgrounds differ from scrolled views. The first library full image omits the New York cover; the second omits several covers. `library-desktop-middle.png` shows the New York cover loading in normal scrolling. Blank capture regions are **not missing source assets** and should not be reproduced.
- Musings displays four desktop columns at this width despite the template's five-column setting. Use the screenshot together with the responsive CSS.
- No obvious copy changes were noticed relative to the archive; a complete live/source diff was not performed.
- Computed font metrics and loaded font faces were not verified. Chrome blocked a console paste with its self-XSS warning; that protection was left enabled. Existing DESIGN.md measurements remain source declarations.

## Follow-up during implementation

The five additional mobile page captures from the original checklist are no longer required. Font loading and typography verification belong to issue #2; category/author-filter and index-navigation behavior checks belong to the later interactive-behavior work (issue #5). Existing source inventories cover these pages and filters. The accepted scope does not imply those checks were performed or that every saved screenshot was individually inspected. Do not restart the exhaustive capture exercise or re-download the source archive.
