# Dana Enache — Horror Author Website

[![Deploy to GitHub Pages](https://github.com/bogdan1787/dana-enache-website/actions/workflows/update-site.yml/badge.svg)](https://github.com/bogdan1787/dana-enache-website/actions/workflows/update-site.yml)

Live site: **[danaenache.com](https://danaenache.com)**  
GitHub Pages: [bogdan1787.github.io/dana-enache-website](https://bogdan1787.github.io/dana-enache-website/)

---

## Overview

Static horror-author website hosted on GitHub Pages with a custom domain. Features a dark/light theme, a stories collection, books catalogue with purchase buttons, and a comments system (Cusdis). Stories are generated from plain text files — no CMS required.

---

## Project Structure

```
├── index.html              # Homepage
├── about.html              # Author bio
├── stories.html            # Stories listing
├── books/
│   ├── index.html          # Books catalogue
│   ├── evolution/          # Book detail page
│   ├── on-vacation/        # Book detail page
│   └── the-dream/          # Book detail page
├── stories/
│   └── {slug}/
│       ├── index.html      # Generated story page (do not edit manually)
│       ├── story.txt       # Story text (source of truth)
│       └── cover.jpg       # Story cover image
├── images/
│   └── books/              # Book covers + author photo
├── style.css               # Full design system (dark/light themes, all components)
├── script.js               # Main JS (nav, scroll, interactions)
├── theme.js                # Dark/light theme toggle + localStorage
├── blood.js                # Blood-drip canvas animation (homepage)
├── geo-links.js            # Geo-targeted Amazon links
├── generate-story-manifest.py  # Builds all story pages + manifest
├── optimize-images.py      # WebP thumbnail generation
├── story-manifest.json     # Generated — do not edit manually
├── story-dates.json        # Override publication dates per story slug
├── sitemap.xml             # Full sitemap for danaenache.com
├── robots.txt
└── .github/workflows/
    └── update-site.yml     # CI: generate pages → optimize images → deploy
```

---

## Adding a New Story

1. Create a folder under `stories/`:
   ```
   stories/
   └── my-story-title/
       ├── story.txt    ← story text (UTF-8, plain paragraphs)
       └── cover.jpg    ← cover image (recommended: 1200×630)
   ```

2. Optionally set a publication date in `story-dates.json`:
   ```json
   {
     "my-story-title": "2025-06-01"
   }
   ```

3. Push to `main` — the CI pipeline will:
   - Run `generate-story-manifest.py` → builds `stories/{slug}/index.html` + `story-manifest.json`
   - Run `optimize-images.py` → generates WebP thumbnails
   - Deploy to GitHub Pages automatically

> **Never edit generated `stories/{slug}/index.html` directly** — it will be overwritten by CI.

---

## Running Locally

```bash
# Generate story pages
python generate-story-manifest.py

# Optimize images (requires Pillow)
pip install Pillow
python optimize-images.py

# Serve locally (any static server)
npx serve .
# or
python -m http.server 8080
```

---

## CI / Deployment

`.github/workflows/update-site.yml` triggers on every push to `main`:

1. Runs `generate-story-manifest.py`
2. Runs `optimize-images.py`
3. Commits changed files back to `main` (manifest + generated pages)
4. Deploys to GitHub Pages via `actions/deploy-pages`

> **Rebase conflicts**: The CI commits `story-manifest.json` back on every run. When rebasing locally, resolve with `git checkout --ours story-manifest.json`.

---

## SEO

Every page includes:
- Full OpenGraph + Twitter Card meta tags
- `<link rel="canonical">` pointing to `danaenache.com`
- JSON-LD structured data:
  - **Homepage**: `WebSite` + `Person` (with `@id: https://danaenache.com/#author`)
  - **About**: `Person` (canonical author entity) + `BreadcrumbList`
  - **Story pages**: `Article` + `BreadcrumbList` (author cross-linked via `@id`)
  - **Book pages**: `Book` + `BreadcrumbList`
  - **Books listing**: `CollectionPage` + `BreadcrumbList`
- Visual breadcrumb nav on all inner pages
- `sitemap.xml` with image tags for all story/book covers

---

## Theme

- Default: **dark** (horror aesthetic)
- Persisted in `localStorage` key `de-theme`
- Toggled via the moon/sun button in the nav
- Cusdis comments widget theme is synced automatically

---

## Key Integrations

| Feature | Service |
|---------|---------|
| Comments | [Cusdis](https://cusdis.com) (self-hostable, GDPR-friendly) |
| Signed copy / personalized stories | PayPal buttons |
| Books (Amazon) | Geo-targeted links via `geo-links.js` |
| Fonts | Google Fonts (Playfair Display + Inter) |
