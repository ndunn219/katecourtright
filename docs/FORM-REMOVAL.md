# Issue #4: contact and signup removal

The migrated output contains no contact, newsletter, or ARC signup form, submission handler, or signup integration. Earlier migration work already omitted the form blocks and footer signup. Issue #4 completes the copy audit and URL decisions and adds checks against reintroduction. The original Squarespace capture stays unchanged and is never deployed.

## Page decisions

| Location | Decision |
| --- | --- |
| `/contact/` | Retain the hero, invitation, thank-you text, and original Instagram, Facebook, Bookbub, and Goodreads destinations. No form, submission messages, replacement email field, or invented contact address. |
| `/newsletter/` | Retire the signup page’s function. Keep the existing static retirement notice and Musings link at the old URL for bookmarks. It emits `newsletter/index.html` (a normal 200 page, not an HTTP redirect), stays out of desktop/mobile navigation and the sitemap, and has no incoming signup links. Hosted extensionless URL behavior remains a deployment check. |
| `/arc/` | Retain an informational page at the old URL. Replace “Join my … Team” and “I would love to add you” with a neutral explanation, an explicit unavailable-signup notice, and links to the library and Musings. This does not announce that the reader program itself has ended. Keep its canonical URL and sitemap entry; do not add it to primary navigation. |
| `/privacy-policy/` | Replace only the newsletter-collection heading/paragraph with the current absence of the three forms. Retain guidance for unsubscribing from emails already received; removal of website signup does not establish that an existing mailing list was deleted. |
| Shared footer and navigation | Keep the existing form-free footer and common navigation data. No newsletter signup, invitation, submission messages, or reserved form container remains. |

## Site-wide audit

Compared the [captured form inventory](../reference/squarespace/2026-11-07/INVENTORY.md#form-and-signup-locations) with every generated HTML page and deployed script/stylesheet. The source had a shared newsletter block across the captured pages, a Contact form, and an additional ARC signup. Retired template pages remain absent; retained pages, both homepage URLs, all posts, category/author archives, search, and the shared footer contain no signup blocks.

The historical reference to a “previous newsletter” in the Anna Quindlen post remains article content, not an invitation to subscribe. Existing-email unsubscribe guidance remains useful and does not send visitors to a removed website feature. The remaining policy references to analytics, Squarespace, hosting logs, and third-party services require the already-planned final service review in issue #6; this change is not a full policy rewrite. Footer platform credit remains issue #5.

## Verification

`npm run check` passes at both `/` and `/katecourtright/`: 34 HTML pages, 903 internal links/assets, all 39 URL decisions, complete post content, archive membership, EPUB integrity, canonical URLs, sitemap, and legacy author navigation.

The command now also runs `scripts/check_forms.py` against the whole generated HTML/JS/CSS artifact. It checks form embeds, email inputs, known signup integration markers and submission handlers, newsletter links and signup calls to action, retirement notices and reading alternatives, Contact social destinations, and sitemap exclusion. Migration fidelity permits only the two explicit ARC/policy copy replacements; every other captured content block is still checked. Temporary negative fixtures confirmed the audit rejects reintroduced form markup, signup links, integration markup, and JavaScript submission handlers.

Layout review of the templates and responsive CSS found no empty form wrappers, form-only columns, fixed form heights, or signup spacers. Contact keeps its 460px text width and short hero (214px desktop, 96px mobile). ARC uses the existing 950px reading column; its invitation heading becomes normal paragraph copy. Newsletter uses the standard page layout. The existing mobile breakpoint at 640px provides 20px gutters and smaller headings; the footer retains normal content padding. No CSS changes are needed for the removed blocks.

**Browser verification remains unverified.** On November 7, 2026, the computer-use inventory returned “The browser access host is unavailable.” No desktop/mobile screenshots or rendered-layout claims were made. When browser access is restored, inspect Contact, ARC, Newsletter, the policy, and representative shared footers at desktop and mobile widths, including the mobile menu. Font fallback and hosted URL behavior retain their existing launch checks. This implementation does not publish or change the live Squarespace site.
