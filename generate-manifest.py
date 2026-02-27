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
import shutil
from pathlib import Path

IMAGES_DIR   = Path(__file__).parent / "images"
MANIFEST_OUT = Path(__file__).parent / "image-manifest.json"
OG_PREVIEW   = Path(__file__).parent / "og-preview.jpg"
SUPPORTED    = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}

# Matches a leading numeric prefix like "01-", "02_", "003 " etc.
ORDER_PREFIX = re.compile(r"^(\d+)[_\-\s]*")


def slug_to_label(slug: str) -> str:
    words = re.split(r"[-_]+", slug)
    return " ".join(w.capitalize() for w in words if w)


def image_entry(rel: Path, filename: str) -> dict:
    stem  = Path(filename).stem
    # Strip leading numeric order prefix from display name
    clean = ORDER_PREFIX.sub("", stem)
    alt   = re.sub(r"[-_]+", " ", clean).strip() or stem
    return {"file": rel.as_posix(), "alt": alt}


def sort_key(filename: str):
    """Sort by numeric prefix if present, then alphabetically."""
    m = ORDER_PREFIX.match(Path(filename).stem)
    return (int(m.group(1)), filename) if m else (10000, filename)


def scan_dir(directory: Path, slug: str) -> list:
    images = []
    try:
        files = [f for f in directory.iterdir()
                 if f.is_file() and f.suffix.lower() in SUPPORTED]
        files.sort(key=lambda f: sort_key(f.name))
        for f in files:
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
root_files = [e for e in entries if e.is_file() and e.suffix.lower() in SUPPORTED]
root_files.sort(key=lambda f: sort_key(f.name))
root_images = [image_entry(Path("images") / e.name, e.name) for e in root_files]
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

# Auto-copy first image as social preview (og-preview.jpg)
first_img = next(
    (Path(__file__).parent / c["images"][0]["file"]
     for c in categories if c["images"]),
    None
)
if first_img and first_img.exists():
    shutil.copy2(first_img, OG_PREVIEW)
    print(f"   ✓ Social preview → {OG_PREVIEW.name}")

total = sum(len(c["images"]) for c in categories)
print(f"✓  Manifest written → {MANIFEST_OUT.name}")
print(f"   {len(categories)} categor{'ies' if len(categories) != 1 else 'y'}, "
      f"{total} image{'s' if total != 1 else ''}")
for c in categories:
    print(f"   • {c['name']} ({len(c['images'])})")
