#!/usr/bin/env python3
"""Generate smaller WebP variants (<name>-w<width>.webp) for responsive srcset.

Run after adding or replacing an image in src/assets/images/ (requires Pillow):
    python3 scripts/resize_images.py
The `srcset` filter in eleventy.config.js lists whichever variants exist.
Originals are left untouched; their provenance is in docs/asset-provenance.json.
"""
from pathlib import Path
import re
from PIL import Image

WIDTHS = (800, 1600)
for source in sorted(Path('src/assets/images').glob('*.webp')):
    if re.search(r'-w\d+\.webp$', source.name):
        continue
    with Image.open(source) as image:
        for width in WIDTHS:
            target = source.with_name(f'{source.stem}-w{width}.webp')
            if image.width <= width:
                target.unlink(missing_ok=True)
                continue
            height = round(image.height * width / image.width)
            image.resize((width, height), Image.LANCZOS).save(target, 'WEBP', quality=82, method=6)
            print(f'{target} {target.stat().st_size // 1024} KB')
