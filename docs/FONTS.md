# Independent font configuration

Status: **owner-controlled fonts pending**. No Adobe project ID or licensed font files were supplied. No Squarespace kit or font binaries have been copied. Browser font loading and actual rendered faces have not been verified.

The original declarations are preserved in `src/assets/css/site.css`:

| Family | Required faces |
| --- | --- |
| `freight-display-pro` | Light 300, Medium 500, plus italics and bold used by headings and book links |
| `freight-sans-pro` | Regular 400, Medium 500, bold and italic; the representative post uses bold italic |

Default preview stacks are `freight-display-pro, Georgia, serif` and `freight-sans-pro, Arial, sans-serif`. These are explicit temporary fallbacks, not a claim of design equivalence or an approved replacement. They change text widths, wrapping, page height, and perceived weight. Every build without the Adobe ID emits a font warning. No font setup details are placed in visitor-facing page content.

## Adobe Fonts

Supply an owner-controlled project containing the required families/faces, authorized for the relevant domains. Set the seven-character ID from its CSS embed URL:

```sh
ADOBE_FONTS_PROJECT_ID=YOUR_ID npm run build
ADOBE_FONTS_PROJECT_ID=YOUR_ID npm run build:preview
ADOBE_FONTS_PROJECT_ID=YOUR_ID npm run dev
```

`YOUR_ID` is a placeholder; replace it with the real seven lowercase alphanumeric characters. Invalid IDs fail the build. The base layout emits `https://use.typekit.net/<id>.css` only when configured. The local build does not download or bundle provider font files. Set this variable in the eventual CI build environment as well as locally.

After the project is supplied, inspect its CSS family names and available weights. Update `--display` and `--sans` only if the project's family names differ. Confirm loading and rendered fonts in the browser on both the preview and custom-domain paths, including bold italic post text, before judging line breaks and final spacing.

## Licensed self-hosting alternative

With separately licensed WOFF2 files, add them under `src/assets/fonts/` and define `@font-face` rules in `src/assets/css/fonts.css`. Use the family names above and declare each actual weight/style; use relative URLs such as `url('../fonts/freight-display-light.woff2')`. The asset copy includes that directory automatically and relative CSS URLs support both hosting paths. Remove or revise the Adobe-specific warning in `src/_data/site.js` when self-hosting is actually configured and verified.

Licensing options and the original capture's findings are recorded in [the source font report](../reference/squarespace/2026-11-07/FONTS.md). An Adobe-hosted project does not imply permission to copy the font files into this repository.
