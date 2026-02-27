#!/usr/bin/env python3
"""
optimize-images.py
Resizes and compresses images in-place for web delivery.

Run:     python optimize-images.py
Requires: pip install Pillow  (installed automatically if missing)

How it tracks processed images:
  A SHA-256 hash of each file is stored in image-hashes.json.
  On every run, the current hash is compared to the stored one:
    • Hash unchanged  → already compressed, skip entirely
    • Hash changed / new → compress, overwrite, record new hash
  This means each image is compressed exactly once, no matter how
  many times the script or Action runs. Originals are overwritten —
  keep high-res copies on your device / iPad.
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

IMAGES_DIR  = Path(__file__).parent / "images"
HASHES_FILE = Path(__file__).parent / "image-hashes.json"
MAX_PX      = 2400   # max width or height in pixels
JPEG_Q      = 85     # JPEG / WebP quality (0-100)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# Load existing hash registry
hashes: dict = {}
if HASHES_FILE.exists():
    try:
        hashes = json.loads(HASHES_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass

changed = 0
skipped = 0

for img_path in sorted(IMAGES_DIR.rglob("*")):
    if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        continue

    key          = img_path.relative_to(IMAGES_DIR.parent).as_posix()
    current_hash = sha256(img_path)

    if hashes.get(key) == current_hash:
        skipped += 1
        continue  # already compressed by us — never re-compress

    orig_size = img_path.stat().st_size

    try:
        with Image.open(img_path) as img:
            w, h       = img.size
            needs_resize = max(w, h) > MAX_PX

            if not needs_resize and orig_size <= 500_000:
                # Small enough — no visual change needed, just record hash
                hashes[key] = current_hash
                skipped += 1
                continue

            if needs_resize:
                img.thumbnail((MAX_PX, MAX_PX), Image.LANCZOS)

            fmt = img_path.suffix.lower()
            if fmt in {".jpg", ".jpeg"}:
                if img.mode not in ("RGB", "L"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        bg.paste(img, mask=img.getchannel("A"))
                    else:
                        bg.paste(img.convert("RGB"))
                    img = bg
                img.save(img_path, "JPEG", quality=JPEG_Q, optimize=True)
            elif fmt == ".png":
                img.save(img_path, "PNG", optimize=True)
            elif fmt == ".webp":
                img.save(img_path, "WEBP", quality=JPEG_Q, method=6)

        new_size     = img_path.stat().st_size
        saving       = round((1 - new_size / orig_size) * 100) if orig_size else 0
        hashes[key]  = sha256(img_path)   # hash of the compressed version
        print(f"  ✓  {key}  {orig_size // 1024} KB → {new_size // 1024} KB  (−{saving}%)")
        changed += 1

    except Exception as e:
        print(f"  ⚠  {img_path.name}: {e}")

# Persist updated hashes
HASHES_FILE.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

if changed:
    print(f"\n✓  Compressed {changed} image{'s' if changed != 1 else ''}  "
          f"({skipped} already up-to-date).")
else:
    print(f"✓  All {skipped} image{'s' if skipped != 1 else ''} already up-to-date — nothing to do.")

