# Issue #6 verification record

Recorded November 7, 2026. **Preview verified over HTTP; domain cutover pending.**
The updated workflow passed on GitHub, including all local checks, preview
deployment, and verification against the exact published artifact. The report
below was downloaded from that workflow’s `hosted-verification` artifact.

## Concrete results

| Check | Result/evidence |
| --- | --- |
| Dependencies | Issues #1–#5 are closed on GitHub. Existing scope decisions remain in the content, form-removal, font, layout, and interactions documents. |
| Actions preview | [Run 42407667213](https://github.com/ndunn219/katecourtright/actions/runs/42407667213), commit `585792056ee3215e3622e123d1d849a78d243dff`: build, deploy, and hosted verification succeeded. |
| Pages source | Found `build_type=legacy`, causing an additional failing Jekyll workflow. Changed to `workflow` via Pages API and verified the returned setting. |
| Preview HTTPS | `https://ndunn219.github.io/katecourtright/`; Pages reports HTTPS enforced, no custom domain. |
| Published artifact | The deploy job extracted its `github-pages` artifact and compared every public file with HTTP GET responses. **62 checks passed**: 57 file responses at 200, five missing/retired routes at 404 with the exact custom 404 body. See [machine-readable report](verification/preview-http.json). |
| Assets and downloads | All published CSS, JS, images, search JSON, and both EPUBs matched the artifact byte-for-byte. |
| Local builds | `npm run check` passes repository preview, production root, and root preview: 34 pages, 972 local links/assets per build, all 39 URL decisions, 14 posts, archives, anchor targets, metadata, canonical URLs, sitemap, forms, EPUB integrity, and interaction handler checks. |
| Production indexing | Explicit production build enables content indexing. Search, Newsletter notice, and 404 stay noindex. Ordinary and repository previews stay noindex. Production rejects a non-root prefix. |
| Deployment checker tests | Four localhost HTTP regression scenarios: valid artifact/custom 404 passes; soft 404, corrupted download, and redirected content fail. |
| External links | 34 unique content destinations: 25 returned 200, eight returned 403, one returned 404. See [external audit](verification/external-links.json); social sharing composers are excluded. |
| Domain state | Public apex A records still point to `198.185.159.144`, `198.185.159.145`, `198.49.23.144`, `198.49.23.145`; www CNAME is `ext-sq.squarespace.com`. No DNS changes made. |

The original sitemap had the same URL membership but different ordering across
local and CI builds. This implementation sorts its entries. Both the preceding deployment and this updated deployment passed exact-artifact
HTTP comparisons. The saved preview report is from the updated deployment.
Reports are observations at their timestamps, not ongoing availability guarantees.

## External destinations needing review

- Barnes & Noble's First Impressions URL returned **404**:
  `https://www.barnesandnoble.com/w/first-impressions-kate-courtright/1142102527?ean=2940186593102`.
  Confirm a replacement with the owner before changing the preserved retailer URL.
- BookBub author page, Chirp's Pinkie audiobook, and six Kobo destinations returned
  **403**. Browser verification is pending; bot restrictions are possible.
- The report lists each destination, final URL, HTTP status, and originating page.
  No retailer URL has been removed or replaced based solely on this automated audit.

## Browser comparison matrix — pending

The computer-use inventory returned **“The browser access host is unavailable”**
again on November 7. No rendered screenshots or visual equivalence are claimed.
For each row below, compare with the accepted [reference capture](../reference/squarespace/2026-11-07/screenshots/README.md)
at desktop 1440×900 and mobile 390×844; also check overflow at 320px. Where no
matching source screenshot exists, record functional/layout inspection separately.

| Page types | Checks still required |
| --- | --- |
| Home and `/welcome/` alias | Bench crop, overlay header, portrait, teal sections, typography, spacing, anchor scrolling |
| About | Portrait proportions, text wrapping, stacked mobile layout |
| Library and First Impressions | Featured banner, two-column/stacked covers, retailer links, both downloads |
| Works and retained Fire Boy excerpt | Railway crop, long-form text, headings, deep anchors |
| Contact, Newsletter notice, ARC | Intentional signup removal, reader links, spacing without forms |
| Musings, author and category archives | Card columns, dates, membership, heading wrapping, old author query links |
| Blog posts | Bold italic text, heading/date layout, adjacent posts and sharing; inspect all 14 for overflow |
| Search | Empty/results/no-results states, query reload/history, network failure/retry, no-JS directory |
| Privacy and 404 | Readable text, navigation, missing-route behavior |
| Shared UI | Tab/Shift+Tab, skip link, menu Enter/Space/Escape, focus restoration, resize, reduced motion, console errors and blocked Squarespace domains |

Automated DOM-double tests do not establish native browser keyboard behavior,
touch behavior, computed fonts, image crops, or mobile overflow.

## Remaining launch requirements

1. Compare the deployed preview against the redesign canvas rather than the
   Squarespace references (redesign #16). Headless-browser checks of the redesign
   are recorded in [LAYOUT-VERIFICATION.md](LAYOUT-VERIFICATION.md); fonts are
   self-hosted Newsreader and Source Sans 3 ([FONTS.md](FONTS.md)).
2. The privacy policy was replaced with a short policy whose claims are checked
   against the build (redesign #15; see [REDESIGN.md](REDESIGN.md)). Confirm the
   wording with Kate before launch.
3. Review the external destination failures above.
4. Complete the [cutover and rollback procedure](DEPLOYMENT.md) with DNS-provider
   access and a full DNS backup, then verify production apex/www,
   HTTPS, internal URLs and downloads. Keep Squarespace available meanwhile.

Issue #6 must remain open: preview publication is evidenced, but review of the
deployed redesign and custom-domain production verification are not complete.
