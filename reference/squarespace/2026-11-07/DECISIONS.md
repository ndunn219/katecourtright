# Scope decisions and migration findings

These are findings and recommendations, not changes to the live site. Preserve the archived source while deciding what belongs in the replacement.

| Item | Finding | Recommendation / pending decision |
| --- | --- | --- |
| `/listing-01-hatch`, `/listing-03-hatch`, `/listing-04-hatch` | Sample real-estate listings in the public sitemap | Recommend excluding them from the new site; decide explicitly how their old URLs should behave. |
| **`/listing-02-hatch`** | Contains a **Fire Boy chapter-one excerpt**, not a sample property listing | Preserve the excerpt. Retain the legacy path or explicitly choose a new destination and compatible old-URL handling. Do not bulk-delete all `*-hatch` pages. |
| `/schedule-appointment-hatch` | Linked by sample listings; HTTP 404 at capture | Existing source defect. Excluding the sample listings removes the associated dead links. |
| `/arc` | ARC invitation with its own signup, plus the global newsletter block | Remove signup functionality; decide whether to retain the invitation text or retire the page. |
| `/newsletter` | No main content beyond the shared newsletter signup | Retire the signup/navigation entry in issue #4; decide the old URL's destination. |
| `/contact` | Introductory text, photo, reader/social links, and a form | Remove the form and retain the rest by default. |
| `/first-impressions` | Public, unlinked ARC thank-you/download page | Preserve the content and both EPUB download paths unless explicitly retired. Do not add it to the main navigation merely because it was discovered. |
| `/privacy-policy` | Refers to newsletter storage, Squarespace analytics, forms, fonts, and cookies | Preserve the source; review the copy against the actual replacement's services before launch. A verbatim copy may describe services that have been removed. |
| `/` and `/welcome` | Both return the homepage, with canonical root URL | Preserve entry from both paths and keep the root canonical. |
| Blog dates | Displayed publication dates often differ from the year/month/day in the permalink | Import the displayed date independently; do not derive publication dates or new slugs from the legacy path. |
| Blog authors | Seven posts display Kate Dunn; seven display Vasheena Brisbane | Preserve these public attributions unless an editorial correction is requested. Both existing author-filter links are captured. |
| Blog categories | Four public category archives; several posts have no categories | Preserve the existing assignments rather than inferring categories from article topics. |
| Search and header social icons | Markup exists but body settings hide desktop search/social and mobile search icons | `/search` is reachable directly. Preserve the actual visible design; verify in a browser before adding any search control. |
| Font hosting | Freight Display Pro and Freight Sans Pro load through Squarespace's Typekit integration | Choose an owner-controlled Adobe Fonts project or a separate self-hosted webfont license; see [FONTS.md](FONTS.md). |

## Existing content details worth retaining

- The home hero is the Whidbey Island bench photo; the homepage and About page use different portrait assets.
- The library presents five titles: First Impressions, Pinkie, Fire Boy, Former Things, and It's Up to You, New York. Purchase and audio links are preserved in `pages.json` and `external-links.json`.
- First Impressions has two distinct EPUB responses (generic and Kindle); both are archived and should retain their `/s/` paths.
- The Musings introduction sits outside the `<main>` element. Its text is saved separately as `intro_text`; importing only `main_text` would lose it.
- One newsletter block is shared across all 36 successful HTML pages, including search and filtered archives. `/arc` contains a second newsletter block. The contact form is a JavaScript-mounted block; searching only for literal `<form>` elements would miss it.
- Raw source contains a newsletter storage-configuration message. It is source evidence, not a verified visitor-visible error; do not recreate it.
- Footer copy includes a 2019–2025 copyright, Squarespace platform credit, privacy link, and Brisbane Creative attribution. Platform credit changes belong to issue #5; preserve other attribution unless separately changed.

