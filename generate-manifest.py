#!/usr/bin/env python3
"""
generate-manifest.py
Scans the images/ folder and writes image-manifest.json.

Run locally:  python generate-manifest.py
              (Python 3 stdlib only — no packages to install)

Structure expected:
  images/
    category-name/   ← subfolder name becomes the category label
      photo1.jpg
      photo2.png
    another-category/
      ...

Images placed directly in images/ (no subfolder) are grouped
under "General".
"""

import json
import re
from pathlib import Path

IMAGES_DIR   = Path(__file__).parent / "images"
MANIFEST_OUT = Path(__file__).parent / "image-manifest.json"
SUPPORTED    = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}


def slug_to_label(slug: str) -> str:
    words = re.split(r"[-_]+", slug)
    return " ".join(w.capitalize() for w in words if w)


def image_entry(rel: Path, filename: str) -> dict:
    stem = Path(filename).stem
    alt  = re.sub(r"[-_]+", " ", stem).strip()
    return {"file": rel.as_posix(), "alt": alt}


def scan_dir(directory: Path, slug: str) -> list:
    images = []
    try:
        for f in sorted(directory.iterdir()):
            if f.is_file() and f.suffix.lower() in SUPPORTED:
                images.append(image_entry(Path("images") / slug / f.name, f.name))
    except PermissionError:
        pass
    return images


# ── main ──────────────────────────────────────────────────────────────────────

if not IMAGES_DIR.exists():
    IMAGES_DIR.mkdir()
    print("Created images/ folder.")

categories = []
entries    = sorted(IMAGES_DIR.iterdir(), key=lambda e: e.name.lower())

# Images directly in images/ root → "General"
root_images = [
    image_entry(Path("images") / e.name, e.name)
    for e in entries
    if e.is_file() and e.suffix.lower() in SUPPORTED
]
if root_images:
    categories.append({"name": "General", "slug": "general", "images": root_images})

# Subfolders → categories
for entry in entries:
    if entry.is_dir():
        imgs = scan_dir(entry, entry.name)
        if imgs:
            categories.append({
                "name"  : slug_to_label(entry.name),
                "slug"  : entry.name,
                "images": imgs,
            })

manifest = {"categories": categories}
MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

total = sum(len(c["images"]) for c in categories)
print(f"✓  Manifest written → {MANIFEST_OUT.name}")
print(f"   {len(categories)} categor{'ies' if len(categories) != 1 else 'y'}, "
      f"{total} image{'s' if total != 1 else ''}")
for c in categories:
    print(f"   • {c['name']} ({len(c['images'])})")
