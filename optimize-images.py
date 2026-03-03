#!/usr/bin/env python3
"""
optimize-images.py
Resizes and compresses images in-place for web delivery.

Run:     python optimize-images.py
Requires: pip install Pillow  (installed automatically if missing)

Pipeline per image (runs exactly once per unique file, tracked by SHA-256):
  1. Resize to max 2400 px on longest side
  2. Compress  (JPEG/WebP quality 85, PNG lossless)
  3. Record SHA-256 of final file → stored in image-hashes.json

On subsequent runs the hash is unchanged → step skipped entirely.
To re-process an image, delete its entry from image-hashes.json or delete the file entirely.
"""

import hashlib
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess, sys
    print("Installing Pillow…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image

# ── Configuration ─────────────────────────────────────────────────────────────

IMAGES_DIR    = Path(__file__).parent / "images"
HASHES_FILE   = Path(__file__).parent / "image-hashes.json"

MAX_PX         = 2400    # max width or height for full images
THUMB_PX       = 400     # max width or height for grid thumbnails
WEBP_PX        = 600     # max width or height for same-name WebP companion
JPEG_Q         = 85      # JPEG / WebP quality


# ── Helpers ───────────────────────────────────────────────────────────────────

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def save_image(img: Image.Image, path: Path):
    """Save image to path in its native format."""
    fmt = path.suffix.lower()
    if fmt in {".jpg", ".jpeg"}:
        rgb = img.convert("RGB")
        rgb.save(path, "JPEG", quality=JPEG_Q, optimize=True)
    elif fmt == ".png":
        img.save(path, "PNG", optimize=True)
    elif fmt == ".webp":
        img.save(path, "WEBP", quality=JPEG_Q, method=6)


def generate_thumb(img: Image.Image, original_path: Path) -> Path:
    """Save a 400px WebP thumbnail and return its path."""
    thumb_dir = original_path.parent / "thumbs"
    thumb_dir.mkdir(exist_ok=True)
    thumb_path = thumb_dir / (original_path.stem + ".webp")

    # Remove old same-stem non-webp thumb if it exists
    for old in thumb_dir.glob(original_path.stem + ".*"):
        if old.suffix.lower() != ".webp":
            old.unlink()

    thumb = img.copy()
    thumb.thumbnail((THUMB_PX, THUMB_PX), Image.LANCZOS)
    save_image(thumb, thumb_path)
    return thumb_path


def generate_webp_companion(img: Image.Image, original_path: Path) -> Path:
    """Save a 600px WebP alongside the source JPEG/PNG and return its path."""
    webp_path = original_path.with_suffix(".webp")
    companion = img.copy()
    companion.thumbnail((WEBP_PX, WEBP_PX), Image.LANCZOS)
    save_image(companion, webp_path)
    return webp_path


# ── Main ──────────────────────────────────────────────────────────────────────

hashes: dict = {}
if HASHES_FILE.exists():
    try:
        hashes = json.loads(HASHES_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass

changed = 0
skipped = 0

for img_path in sorted(IMAGES_DIR.rglob("*")):
    # Skip thumbnails (they live in thumbs/ subdirs and are auto-generated)
    if "thumbs" in img_path.parts:
        continue
    if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        continue

    key          = img_path.relative_to(IMAGES_DIR.parent).as_posix()
    current_hash = sha256(img_path)

    # Support both old (string) and new (dict) hash format
    stored = hashes.get(key)
    stored_hash = stored if isinstance(stored, str) else (stored or {}).get("hash")
    if stored_hash == current_hash:
        skipped += 1
        continue  # already processed — never re-compress or re-watermark

    orig_size = img_path.stat().st_size

    try:
        with Image.open(img_path) as img:
            w, h = img.size
            if max(w, h) > MAX_PX:
                img.thumbnail((MAX_PX, MAX_PX), Image.LANCZOS)
            final_w, final_h = img.size
            result = img.copy()

        save_image(result, img_path)
        generate_thumb(result, img_path)
        if img_path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            generate_webp_companion(result, img_path)

        new_size    = img_path.stat().st_size
        saving      = round((1 - new_size / orig_size) * 100) if orig_size else 0
        hashes[key] = {"hash": sha256(img_path), "w": final_w, "h": final_h}
        print(f"  ✓  {key}  {orig_size // 1024} KB → {new_size // 1024} KB  (−{saving}%)")
        changed += 1

    except Exception as e:
        print(f"  ⚠  {img_path.name}: {e}")

# Prune stale hashes for deleted images (exclude thumbs from live_keys)
live_keys = {
    img_path.relative_to(IMAGES_DIR.parent).as_posix()
    for img_path in IMAGES_DIR.rglob("*")
    if "thumbs" not in img_path.parts
    and img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
}
pruned = {k for k in hashes if k not in live_keys}
if pruned:
    hashes = {k: v for k, v in hashes.items() if k in live_keys}
    print(f"  Pruned {len(pruned)} stale hash entr{'ies' if len(pruned) != 1 else 'y'}.")

HASHES_FILE.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

if changed:
    print(f"\n✓  Processed {changed} image{'s' if changed != 1 else ''}  "
          f"({skipped} already up-to-date).")
else:
    print(f"✓  All {skipped} image{'s' if skipped != 1 else ''} already up-to-date — nothing to do.")

