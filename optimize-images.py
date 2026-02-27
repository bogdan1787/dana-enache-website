#!/usr/bin/env python3
"""
optimize-images.py
Resizes and compresses images in-place for web delivery.

Run:     python optimize-images.py
Requires: pip install Pillow  (installed automatically if missing)

Rules:
  • Skips images already ≤ 2400 px AND ≤ 500 KB
  • JPEG / WebP → recompressed at quality 85
  • PNG          → lossless re-saved (size still reduced by removing metadata)
  • Originals are overwritten — keep high-res copies on your device / iPad
"""

from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess, sys
    print("Installing Pillow…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image

IMAGES_DIR  = Path(__file__).parent / "images"
MAX_PX      = 2400      # max width or height in pixels
JPEG_Q      = 85        # JPEG / WebP quality (0-100)
SIZE_LIMIT  = 500_000   # bytes — skip file if already small enough

changed = 0

for img_path in sorted(IMAGES_DIR.rglob("*")):
    if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        continue
    try:
        orig_size = img_path.stat().st_size
        with Image.open(img_path) as img:
            w, h = img.size
            if max(w, h) <= MAX_PX and orig_size <= SIZE_LIMIT:
                continue  # already fine

            if max(w, h) > MAX_PX:
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

        new_size = img_path.stat().st_size
        saving   = round((1 - new_size / orig_size) * 100) if orig_size else 0
        rel      = img_path.relative_to(IMAGES_DIR.parent)
        print(f"  ✓  {rel}  {orig_size // 1024} KB → {new_size // 1024} KB  (−{saving}%)")
        changed += 1

    except Exception as e:
        print(f"  ⚠  {img_path.name}: {e}")

if changed:
    print(f"\n✓  Optimized {changed} image{'s' if changed != 1 else ''}.")
else:
    print("✓  All images already optimized — nothing to do.")
