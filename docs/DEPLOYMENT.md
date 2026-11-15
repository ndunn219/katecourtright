# Deployment, updates, and rollback

Issue #6 implementation and evidence: [verification record](DEPLOYMENT-VERIFICATION.md).
The custom-domain cutover is pending the launch requirements in that record.

## Build and publish

Requires Node.js 20+, npm, Python 3.9+, and curl. `npm run check` uses a temporary
localhost HTTP server for its deployment-check regression tests; it makes no
external requests.

| Command/configuration | Hosting path | Indexing |
| --- | --- | --- |
| `npm run build` | `/` by default, or `SITE_PATH_PREFIX` | Preview by default |
| `npm run build:preview` | `/katecourtright/` | Always disabled |
| `npm run build:production` | `/` | Enabled for retained content |
| `npm run check` | Repository preview, production root, root preview | Checks all three; leaves root preview |

Production excludes Search, the retired Newsletter notice, and 404 from indexing.
The homepage alias keeps the canonical homepage URL. Canonical and social URLs
always refer to `https://katecourtright.com`; sitemap entries are sorted for
reproducible builds. Preview remains publicly accessible despite `noindex`.

The Actions workflow installs the lockfile with `npm ci`, runs checks, builds the
selected configuration, and uploads only `_site/`. `SITE_ENV`, a repository
Actions variable, defaults to `preview`. Set it to `production` only for the
cutover. The workflow checks that the configured Pages URL matches the selected
mode and fails on an inconsistent setup. Fonts are self-hosted and need no
build variables; see [FONTS.md](FONTS.md).

Pages **Source must be GitHub Actions**, not deployment from the `main` branch.
This was corrected on November 7, 2026. For preview, keep the custom domain empty.
A push to `main` or a manual workflow run on `main` publishes the site.

After deployment, the workflow downloads the exact Pages artifact and checks
every published page and asset, including EPUBs, JSON search data, and sitemap.
It also checks the custom 404 body and HTTP status for a nested missing URL and
all retired inventory routes. Redirects, incorrect status codes, and differing
file hashes fail verification. It retries three times for CDN propagation and
saves `hosted-verification` as an Actions artifact. A failed verification after
deployment means the deployment may already be live; inspect its report and
roll back if necessary. It does not automatically restore the previous site.

## Repeat verification

Use the exact deployment artifact for byte comparisons. A local build must use
the same commit, fonts, and hosting mode as the deployed site.

```sh
npm ci
npm run check
npm run build:preview
python3 scripts/check_hosted.py \
  --base-url https://ndunn219.github.io/katecourtright/ \
  --report /tmp/preview-http.json
python3 scripts/check_hosted.py --external --report /tmp/external-links.json
```

For an extracted Pages artifact, add `--output-dir /path/to/extracted/site`.
For production, build with `npm run build:production` and use
`--base-url https://katecourtright.com/`. Do not compare a root build to the
repository-path preview. Old artifacts can have a different sitemap order;
the checker deliberately reports any byte difference.

External-link checks issue GET requests, follow redirects, record originating
pages, and return nonzero for review items. They skip social sharing composers;
sharing URL construction is covered by the offline checks. HTTP 403 can indicate
bot restrictions; successful HTTP responses do not prove the destination's
content is correct. Browser review remains necessary.

## DNS and registrar

DNS for `katecourtright.com` is hosted by **Cloudflare** in Nat Dunn's account
(nameservers `hans.ns.cloudflare.com` and `piper.ns.cloudflare.com`, switched at
Squarespace on November 14, 2026). The registration is moving from Squarespace to
Cloudflare Registrar; see issue #19. Make all DNS changes in the Cloudflare
dashboard. Squarespace's DNS panel no longer applies.

Keep every record **DNS only** (grey cloud). GitHub Pages issues its own HTTPS
certificate and needs DNS to resolve directly to GitHub; Cloudflare's proxy is
optional and can be considered only after HTTPS is enforced and verified.

Records before the GitHub Pages cutover (Cloudflare import, verified against
Squarespace and public DNS on November 14, 2026; TTL Auto). This is the rollback
reference for the website records:

| Type | Name | Content | Purpose |
| --- | --- | --- | --- |
| A | `@` | `198.185.159.144`, `198.185.159.145`, `198.49.23.144`, `198.49.23.145` | Squarespace site |
| CNAME | `www` | `ext-sq.squarespace.com` | Squarespace site |
| CNAME | `_domainconnect` | Squarespace Domain Connect | Squarespace; removable after transfer |
| MX | `@` | `aspmx.l.google.com` (1), `alt1`/`alt2.aspmx.l.google.com` (5), `alt3`/`alt4.aspmx.l.google.com` (10) | Google email |
| TXT | `@` | `v=spf1 include:squarespace-mail.com ~all` | SPF |
| TXT | `_dmarc` | `v=DMARC1; p=none` | DMARC |

## Domain cutover

Proceed after the verification record's unresolved requirements are complete,
or after the owner accepts launching with them open. Keep Squarespace hosting
active throughout cutover and production verification.

1. Confirm Cloudflare shows the zone as **Active** and the `.com` registry lists
   only the Cloudflare nameservers:
   `dig +norec katecourtright.com NS @a.gtld-servers.net`. Record the last good
   Pages deployment SHA and the repository Actions variables.
2. Verify ownership in the GitHub **account** settings (Settings → Pages →
   Add a domain), not the repository settings. Add GitHub's supplied
   `_github-pages-challenge-…` TXT record in Cloudflare (DNS only), wait for it to
   resolve, then click **Verify**. Retain that record. Do not guess its value.
3. In Cloudflare, replace only the website-routing records. Delete the four
   Squarespace A records and add four apex A records: `185.199.108.153`,
   `185.199.109.153`, `185.199.110.153`, and `185.199.111.153`. Edit the `www`
   CNAME to `ndunn219.github.io` (without a repository path). All DNS only.
   Do not touch MX, SPF, DMARC, or other records. Recheck the current GitHub
   documentation before applying these values.
4. In repository Settings → Pages, save `katecourtright.com` as the custom
   domain, and set the repository Actions variable `SITE_ENV=production`. Adding
   the custom domain redirects the repository preview, and the site shows a
   GitHub 404 until the production deployment completes, so continue promptly.
5. Wait for GitHub's DNS check and certificate provisioning (it took minutes on
   November 14, 2026), then enable **Enforce HTTPS** in Pages. Run the workflow on
   the reviewed `main` commit only after that: until HTTPS is enforced, the Pages
   URL is `http://katecourtright.com` and the production build deliberately fails
   its URL check without deploying. Verify both apex and www certificates,
   HTTP → HTTPS, and www → apex redirects, including a deep post URL. Check
   Cloudflare's authoritative answers and multiple recursive resolvers; cached
   Squarespace records can persist through their TTL.
6. Rerun the workflow and hosted checker at the custom domain. Review the browser
   matrix, keyboard navigation, search queries, and both EPUB downloads on the
   live site. Confirm there are no `/katecourtright/` asset paths in production.
   Confirm email and unrelated records match the table above. Record the
   successful run, date, SHA, DNS results, and HTTPS results before marking
   issue #6 complete. Retain Squarespace until all verification passes.

GitHub Actions publishing does not require a `CNAME` file; Pages settings own the
custom domain. See GitHub's [domain configuration](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site),
[ownership verification](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages),
and [HTTPS configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).

## Content updates

Edit `src/` following the [README](../README.md#edit-the-site), run `npm run check`,
and review the changed pages locally with `npm run dev`. Commit and push the
reviewed change to `main`; inspect the deployment and hosted verification jobs.
For renderer, CSS, font, or interaction changes, repeat the relevant desktop and
mobile browser checks. Run the external-link audit for retailer/link changes.
Do not edit `_site/`, which is regenerated, or publish `reference/`.

## Rollback

For a code regression on GitHub Pages, revert the offending commit(s) with
`git revert`, review the revert, and push to `main`. Keep the current production
variable and domain settings. Verify the resulting deployment; do not rewrite
shared history or assume rerunning an old preview workflow produces a valid
custom-domain build.

For a failed domain cutover, restore in Cloudflare only the prior website
records from the table under [DNS and registrar](#dns-and-registrar) (DNS only). Leave all email records unchanged. Keep Squarespace
active and verify its site/certificate at apex and www after propagation. Keep
the GitHub custom-domain association until DNS no longer routes to GitHub; then
remove that domain, restore `SITE_ENV=preview`, and rerun the current workflow to
restore the repository preview. Retain the ownership-verification TXT record.
DNS rollback is subject to caching; keep both hosts available during that period.
