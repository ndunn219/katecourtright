# Issue #3 content migration

All 37 captured page/filter URLs have an explicit destination or retirement decision. The two EPUB URLs are preserved as well. [url-migration.json](url-migration.json) records all 39 entries and is checked against the original inventory. The capture remains unchanged; builds read only `src/`.

## Content and scope decisions

| Content | Implementation |
| --- | --- |
| Home, About Kate, Short Stories & Novellas, Works in Progress, Contact | Retain the existing migrated copy, images, and retailer links; preserve source document titles. Original Instagram and Facebook destinations are available as text links on Contact. |
| All 14 posts | Full rich HTML bodies, emphasis, lists, dividers, content links, original titles, and displayed dates. Seven retain the Kate Dunn attribution and seven retain Vasheena Brisbane. None of the captured post bodies contained images. |
| Musings index | Generated in descending displayed publication date order from the post files, not dates embedded in URLs. |
| Four category archives | Preserve the exact assignments, case, and literal `+` characters in legacy paths. Uncategorized posts stay uncategorized. |
| Two author filters | Static `/musings/author/<original-id>/` archives. Original `/musings?author=<id>` links are recognized by a small script and replaced with the corresponding archive URL. |
| `/arc/` | Retain as an informational ARC page. Issue #4 replaces the invitation with a neutral explanation, states that signup is unavailable, and links to the library and Musings. No form or submission messages. |
| `/first-impressions/` | Keep the thank-you/review text, original retailer links, linked cover, and both EPUB files. Add clearly labeled download links. Do not add this page to primary navigation. |
| `/listing-02-hatch/` | Keep the full Fire Boy excerpt at the original path, its original browser title, and the `#listing-02-info` anchor. The original empty “Read the Book” button now leads to the book library. |
| `/listing-01-hatch`, `/listing-03-hatch`, `/listing-04-hatch` | Retire unrelated sample real-estate listings. No output files are emitted for these paths; GitHub Pages serves the shared `404.html`. |
| `/schedule-appointment-hatch` | Already 404 in the capture; remains absent and uses the shared 404. |
| `/newsletter/` | Retire signup. Keep a notice at the old URL linking readers to Musings; exclude it from the sitemap. |
| `/privacy-policy/` | Issue #4 updates only the form/newsletter collection paragraph to reflect removal and retain existing-email unsubscribe guidance. The other original policy text is preserved; review hosting, Squarespace, analytics, and font claims against final services before launch. |
| `/search/` | Preserve a useful destination listing retained pages, posts, categories, and authors. Query-based search remains issue #5; this page does not claim to return search results. Exclude it from the sitemap for now. |

The three podcast links routed through `engage.squarespace-mail.com` now point directly to the original destinations encoded in their `u` parameters. Other external content and retailer links are retained. Squarespace social-sharing widgets and like counters are not article content and remain in issue #5's behavior scope.

## URL handling and metadata

Page output uses `<legacy-path>/index.html`, with a trailing-slash canonical URL. Extensionless old page URLs resolve to these directories on GitHub Pages; the dated blog paths themselves are unchanged. Category paths retain their literal plus signs (not spaces). EPUBs remain files at `/s/First-Impressions-Generic.epub` and `/s/First-Impressions-Kindle.epub` with byte-identical contents.

Both `/` and `/welcome/` render the same homepage; `/welcome/` canonicals to `/`. All pages have absolute production canonicals at `https://katecourtright.com`, including in repository-prefix previews. The sitemap lists each retained canonical page and generated archive once, excluding `/welcome/`, the 404, the newsletter notice, and the temporary search directory. Preview pages remain `noindex, nofollow` until launch review.

Source document titles are preserved, including the long Musings/category titles and the legacy “Listing 02” title. Empty source descriptions use the shared site description. Open Graph metadata describes each page, and posts include their author and publication date. Layouts use local URLs for navigation and asset references, so both `/` and `/katecourtright/` builds work.

GitHub Pages does not execute server-side redirects or query routing. Retired template pages intentionally produce a real 404 using the shared error page, rather than a successful placeholder. Newsletter retirement uses a visible notice with status 200. Author-query compatibility is a client-side navigation, not an HTTP redirect. Known IDs resolve to static archives; unknown/empty IDs leave the full index intact. With JavaScript disabled, the full index and its visible author archive links remain usable. The script reads generated link destinations, preserving the preview prefix. Verify deployed trailing-slash and 404 HTTP behavior during issue #6; local artifact checks do not establish hosted response codes.

## Editing and verification

Post metadata and HTML content live together in `src/posts/*.njk`. For example:

```text
---json
{
  "layout": "layouts/blog-post.njk",
  "tags": ["posts"],
  "title": "Post title",
  "permalink": "/musings/2023/6/30/legacy-slug/",
  "published": "2022-07-01",
  "author": "Vasheena Brisbane",
  "authorId": "536510cee4b043dbe028347e",
  "categories": ["My Sharing Shelf"]
}
---
<p>Editable post content.</p>
```

Kate Dunn's ID is `5c8160afdb7926584fdf6899`. Preserve existing IDs because they are part of public author links. `eleventy.config.js` generates collections and adjacent-post navigation; `src/authors.njk` and `src/categories.njk` render the archives. Page copy is editable under `src/`, book cards in `src/_data/books.json`, and shared layouts under `src/_includes/`. No capture parser or archived HTML is used during production builds.

`npm run check` passed for both `/` and `/katecourtright/`: 34 HTML pages and 903 internal links/assets per build after issue #4. The migration checks independently compare generated content with the accepted archive, covering every original text block on retained pages with explicit, narrow expectations for the issue #4 ARC and policy edits, all 14 complete post bodies, source titles, content/retailer links, dates, authors, categories, and index/archive order. They verify URL inventory coverage, canonical and sitemap destinations, both EPUB hashes and ZIP/package integrity, and script behavior for both legacy author IDs, missing/empty/unknown IDs, extra query parameters, and hosting prefixes. Capture-fidelity assertions intentionally flag later editorial changes; update the baseline expectations deliberately when such changes are authorized.

Browser visual/interaction QA was not performed for this issue. The earlier browser-access limitation and font fallback remain documented in [LAYOUT-VERIFICATION.md](LAYOUT-VERIFICATION.md) and [FONTS.md](FONTS.md). External destinations were preserved but not checked for current availability.

## Coordination with later issues

- **Issue #4:** implemented; see [form-removal audit](FORM-REMOVAL.md) for the final Contact, Newsletter, and ARC decisions, regression checks, and browser-verification limit.
- **Issue #5:** reuse the implemented author-query compatibility; finish search, remaining interactions, and the platform-credit change. Category and author pages work without Squarespace runtime dependencies.
- **Issue #6:** deploy the output, verify hosted URL/404 behavior and EPUB delivery, complete browser/font checks, review policy/metadata, and only then enable indexing. This change does not deploy or modify the live site.
