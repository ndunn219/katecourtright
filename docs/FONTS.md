# Fonts

Status: **self-hosted, open-source fonts** (redesign decision recorded November 7, 2026).

| Role | Family | Faces | CSS token |
| --- | --- | --- | --- |
| Display: headings, brand, ledes, excerpts | [Newsreader](https://github.com/productiontype/Newsreader) | Variable roman + italic, `opsz` and `wght` axes (200–800) | `--display: 'Newsreader', Georgia, serif` |
| Body and interface | [Source Sans 3](https://github.com/adobe-fonts/source-sans) | Variable roman + italic, `wght` axis (200–900) | `--sans: 'Source Sans 3', system-ui, sans-serif` |

The design uses Newsreader at 400–600 and Source Sans 3 at 400–700. Optical sizing (`opsz`) is applied automatically by browsers through `font-optical-sizing: auto`.

## Files and licensing

- WOFF2 files live in `src/assets/fonts/newsreader/` and `src/assets/fonts/source-sans-3/`, copied unmodified from the Fontsource npm packages `@fontsource-variable/newsreader@5.3.0` (the `opsz` files, which include the weight axis) and `@fontsource-variable/source-sans-3@5.3.1` (the `wght` files).
- Only the **Latin** and **Latin Extended** subsets are committed: four files per family (roman/italic × two subsets). `unicode-range` makes browsers fetch the Latin Extended files only for pages that use those characters.
- Both families are licensed under the **SIL Open Font License 1.1**. The license text sits next to the files as `OFL.txt` and is deployed with them. The OFL permits bundling and redistributing the fonts with the site; it forbids selling the fonts by themselves.

## How they load

- `src/assets/css/fonts.css` declares each `@font-face` with `font-display: swap` and URLs relative to the stylesheet (`../fonts/...`), so the same CSS works at the domain root and under the `/katecourtright/` repository preview path.
- `src/_includes/layouts/base.njk` preloads the two most-used files (Source Sans 3 Latin roman and Newsreader Latin roman). The italics and Latin Extended files load on demand.
- No request goes to Adobe Fonts, Google Fonts, or any other font host, so visitors' IP addresses are not shared with a font provider. `scripts/check_site.py` (run by `npm run check`) fails if generated HTML, CSS, JS, or JSON mentions a third-party font host, if a font file referenced by `fonts.css` is missing or is not WOFF2, or if a license file is missing.
- No build variables or accounts are involved. The earlier `ADOBE_FONTS_PROJECT_ID` option and its build warning have been removed.

## Updating

To update a family, download the new Fontsource package (`npm pack @fontsource-variable/<name>`), copy the same Latin/Latin Extended files over the existing ones, and update the version numbers here and in the comment at the top of `fonts.css`. Keep the `unicode-range` values in sync with the package's CSS. To add another subset, add its files and a matching `@font-face` block.
