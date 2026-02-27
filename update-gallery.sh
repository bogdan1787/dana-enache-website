#!/usr/bin/env bash
# update-gallery.sh — Run from the ArtistWebPage folder
#
# chmod +x update-gallery.sh && ./update-gallery.sh
#
# Requires Python 3 (pre-installed on macOS/Linux).
# If you push images to GitHub instead, the Action does this for you.

if command -v python3 &>/dev/null; then
  PYTHON=python3
elif command -v python &>/dev/null; then
  PYTHON=python
else
  echo "ERROR: Python is not installed. Download it from https://python.org"
  exit 1
fi

if ! $PYTHON -c "import PIL" &>/dev/null 2>&1; then
  echo "Installing Pillow image library..."
  $PYTHON -m pip install Pillow --quiet
fi

$PYTHON optimize-images.py
$PYTHON generate-manifest.py

echo ""
echo "Done! Refresh index.html in your browser to see the updated gallery."
