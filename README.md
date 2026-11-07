# Kate Courtright website migration

Recreate [katecourtright.com](https://katecourtright.com) with Eleventy and GitHub Pages, preserving the existing appearance and content except for the contact form and newsletter signup.

Implementation is tracked in [issues #1–#6](https://github.com/ndunn219/katecourtright/issues). Eleventy implementation has not started; this checkout currently contains the source capture for issue #1.

## Source capture

Start with the [capture report](reference/squarespace/2026-11-07/README.md), then the [page inventory](reference/squarespace/2026-11-07/INVENTORY.md) and [design notes](reference/squarespace/2026-11-07/DESIGN.md).

The archive is reference material, **not the deployable website**. Its raw HTML retains the original forms, external scripts, and Squarespace URLs. Keep `reference/` outside the future Eleventy input/output and GitHub Pages deployment artifact.

Requires Python 3.9+ and curl; no Python packages are needed.

```sh
# Resume the capture, reusing successful responses.
python3 scripts/capture_squarespace.py

# Regenerate inventories entirely from the captured files.
python3 scripts/capture_squarespace.py --offline

# Verify archive integrity, content coverage, and EPUB files.
python3 scripts/verify_capture.py
```

For a later capture, pass a new dated directory with `--output reference/squarespace/YYYY-MM-DD`. Use `--refresh` only when deliberately replacing responses in an existing snapshot. Failed URLs are retried on an online run; `--offline` reuses their recorded status.

Desktop references for all eight requested pages and representative mobile references are saved. The [capture notes](reference/squarespace/2026-11-07/screenshots/README.md) and manifest record inspected images and capture limitations. The representative set was accepted and issue #1 closed on November 7, 2026; the exhaustive capture checklist is retired.

