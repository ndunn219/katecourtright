# Design reference from archived HTML and CSS

These measurements are **source declarations, not computed browser styles or screenshot measurements**. Template variants, body classes, inline block styles, media queries, and font loading affect the final result. Use the raw CSS/HTML together with the captured screenshots during issue #2.

The site template ID is `55f0aac0e4b0f0a5b7e0b22e`. The complete body classes, template settings, controllers, and per-image attributes are saved in `pages.json`; all seven referenced stylesheets and the template bundle are archived.

## Typography and colors

| Element | Family | Weight | Size | Line height | Letter spacing |
| --- | --- | ---: | ---: | ---: | ---: |
| Body | Freight Sans Pro | 400 | 15px | 1.8em | .03em |
| Site title | Freight Display Pro | 500 | 38px | .8em | .06em |
| Desktop primary navigation | Freight Display Pro | 500 | 20px | 1em inherited from nav | .05em |
| Mobile overlay navigation | Freight Display Pro | 500 | 25px | 1.5em | .05em |
| H1 | Freight Display Pro | 300 | 50px | 1.25em | .025em |
| H2 | Freight Display Pro | 300 | 30px | 1.4em | .024em |
| H3 | Freight Sans Pro | 400 | 12px | 4em | .3em, uppercase |
| Blog list title | Freight Display Pro | 300 | 25px | 1.5em | .05em |
| Blog post title | Freight Display Pro | 300 | 40px | 1.4em | .024em |

Body text is `#7a7d7f`; H1/H3 and blog titles use `#3d6870`. H2 uses `rgba(61,104,112,.6)`. Main/header backgrounds are white. `a` inherits color and has no underline by default; more specific block/navigation rules may override this.

At `max-width:640px`, H1 becomes 32px and H2 becomes 28px. The source's letter-spacing overrides are `.016px` and `.0224px` respectively; preserve the reference when implementing rather than assuming these are em values.

## Layout and breakpoints

Main and index content declare desktop padding of `100px 150px`. Intro content declares `50px 150px`; the footer declares `50px 150px`. Main and index vertical padding reduces to 60px on small screens, with additional image-section rules.

| Viewport condition | Main/intro/index horizontal padding |
| --- | ---: |
| Wider than 1024px | 150px |
| At most 1024px | 64px |
| At most 960px | 48px |
| At most 768px | 36px |
| At most 640px | 20px |

The template mobile breakpoint is 640px. Header layout has its own spacing rules; do not apply the content padding table directly to it. The source includes Squarespace's 12-column block grid and page-specific spacer blocks.

Source body settings put desktop branding and primary navigation in the bottom-left header area and Musings in secondary navigation on the bottom right. Desktop search and social icons are hidden. Mobile branding and menu icon are configured in the top-center area, with search hidden. The mobile overlay slides from the right and has a close control. Visual positions and wrapping remain to be verified.

## Page structure and assets

| Page | Structure / important source assets |
| --- | --- |
| `/`, `/welcome` | `#intro` and `#reviews` index sections; bench hero, square author portrait, and a square secondary background |
| `/about-late` | Biography and a different author portrait; reader/social links |
| `/short-stories-novellas` | `#library` index section; First Impressions promo banner, four other book covers, retailer/audio links |
| `/works-in-progress` | Photo plus long text, nested headings, chapter excerpts, and blockquotes |
| `/musings` | Large introduction in `.Intro` outside `<main>`, then 14 post entries |
| Blog post | Title/body/metadata and previous/next navigation; preserve actual publication dates independently of URL dates |
| `/contact` | Photo, invitation text, reader/social links, JavaScript-mounted contact form |
| `/first-impressions` | ARC thank-you text, cover image, and two EPUB download links |

The bench image declares `2500x1875`, both square home images `2500x2500`, and the Musings intro image `1000x563`. The library promo banner is `2362x1594`; Pinkie, Fire Boy, and It's Up to You, New York declare `1563x2500`; Former Things declares `1733x2772`. These are **HTML image dimensions**, not independently measured master-image dimensions. Main-page images use source focal points `0.5,0.5`; all recorded focal points are in `assets.json` occurrences.

Some images appear only in the sitemap or sample-template pages. `referenced_by` distinguishes their provenance. Do not add sitemap-only images to a visible layout without checking the live reference.

## Source-declared behavior

- Index pages use `IndexFirstSectionHeight`, `Parallax`, and `IndexNavigation` controllers. Background-image sections are configured for at least `100vh`; parallax is enabled and index navigation is on the right.
- The site enables Squarespace AJAX navigation. The future site can use ordinary navigation while retaining the visible behavior required by the reference.
- The blog is configured as a grid with five columns and 50px spacing at the template level; responsive rules and the actual content determine its rendered layout. Title/body/metadata visibility is controlled by body classes, not isolated default `display:none` declarations.
- The template has a 480ms opacity entrance animation for intro/main/index content and 170ms navigation color/background transitions.
- Gallery defaults include 3:2 aspect ratio, auto-crop, fade, bullets, and arrows. These defaults do not prove that a retained page uses a gallery; sample real-estate galleries should not drive the author-site implementation.
- `/search` and author-query archives depend on Squarespace server/runtime behavior. Their source is saved, but behavior has not been exercised in a browser.

## Browser observations — November 7, 2026

These are visual observations, separate from the source declarations above. See the [capture notes and metadata](screenshots/README.md).

- At 1440 × 900, desktop branding wraps onto two lines; navigation wraps Newsletter and Contact onto a second row. The homepage header overlays the hero and scrolls away rather than remaining pinned. Musings is a separate button on hero headers; it is absent from the inspected white-header full-page views.
- The 390 × 844 mobile header shows a centered single-line title and a menu icon to its left. The white menu overlay has an X in the upper left, large serif links (the library link wraps), and a smaller sans-serif Musings link. Open, close, and About-link navigation were exercised successfully.
- Home and About use different portraits, as inventoried. Mobile About stacks portrait above biography. Contact stacks invitation above the form; the two name inputs remain side by side. No forms were submitted.
- The newsletter is a pale gray panel with inputs in a desktop row and a mobile column. Copyright and platform/privacy/design credits sit below it. No newsletter configuration error was visible in inspected screenshots.
- Musings has **four columns** at 1440px, not five. The template setting alone does not establish the rendered column count. The representative post visibly includes its October 1, 2023 date, sharing controls, and next-post link; the URL date is different, as already inventoried.
- Screenshots show loaded hero/portrait images and serif/sans typography, but do not establish which font faces rendered. Computed styles and font loading remain unverified; do not label the source table as browser measurements.
- Full-page capture changes parallax/lazy-image rendering. Home background boundaries and blank library cover regions in full captures are capture limitations; compare the scrolled viewport evidence and original assets. No missing asset is inferred from a blank screenshot region.

The original detailed checklist still lacks five mobile pages, category/author behavior, index navigation, and computed typography checks. The source archive remains authoritative for content and CSS declarations. No obvious copy change was noticed, but no complete source/live diff was performed.

