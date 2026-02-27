#!/usr/bin/env bash
# update-gallery.sh — Run from the ArtistWebPage folder
#
# chmod +x update-gallery.sh && ./update-gallery.sh
#
# Requires Python 3 (pre-installed on macOS/Linux) — no packages needed.
# If you push images to GitHub instead, the Action does this for you.

if command -v python3 &>/dev/null; then
  python3 generate-manifest.py
elif command -v python &>/dev/null; then
  python generate-manifest.py
else
  echo "ERROR: Python is not installed. Download it from https://python.org"
  exit 1
fi

echo ""
echo "Done! Refresh index.html in your browser to see the updated gallery."
