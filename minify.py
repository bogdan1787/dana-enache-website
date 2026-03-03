#!/usr/bin/env python3
"""
minify.py — Minify CSS and JS assets into *.min.* files.
Run this whenever you edit style.css or any .js file.
"""
import os
import rcssmin
import rjsmin

ROOT = os.path.dirname(__file__)

CSS_FILES = ['style.css']
JS_FILES  = ['theme.js', 'geo-links.js', 'blood.js', 'goodreads-ratings.js', 'script.js']


def minify_file(src, minify_fn):
    dst = src.replace('.css', '.min.css').replace('.js', '.min.js')
    with open(os.path.join(ROOT, src), encoding='utf-8') as f:
        source = f.read()
    minified = minify_fn(source)
    out_path = os.path.join(ROOT, dst)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(minified)
    original_kb  = len(source.encode()) / 1024
    minified_kb  = len(minified.encode()) / 1024
    saving_pct   = 100 * (1 - minified_kb / original_kb)
    print(f"  {src:<25} {original_kb:5.1f} KB  →  {minified_kb:5.1f} KB  ({saving_pct:.0f}% saved)  →  {dst}")


if __name__ == '__main__':
    print("Minifying CSS...")
    for f in CSS_FILES:
        minify_file(f, rcssmin.cssmin)

    print("Minifying JS...")
    for f in JS_FILES:
        minify_file(f, rjsmin.jsmin)

    print("\nDone. Commit the .min.* files alongside your source files.")
