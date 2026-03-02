import os
import json
import html
import re
from datetime import datetime

URL_RE = re.compile(r'(https?://\S+)')

STORIES_DIR   = 'stories'
MANIFEST_FILE = 'story-manifest.json'
DATES_FILE    = 'story-dates.json'

KNOWN_RO_SLUGS = {
    'naluca', 'constanta', 'omul-verde', 'copilul-din-vis',
    'oameni-cu-fete-monotone', '3'
}
SPECIAL_TITLES = {
    '3': '3',
    'naluca': 'Năluca',
    'constanta': 'Constanța',
    'omul-verde': 'Omul Verde',
    'copilul-din-vis': 'Copilul din Vis',
    'oameni-cu-fete-monotone': 'Oameni cu Fețe Monotone',
    'back-to-life': 'Back to Life',
    'the-little-ones': 'The Little Ones',
    'last-breath': 'Last Breath',
}
RO_DIACRITICS = set('ăâîșț')

STORY_PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — Dana Enache</title>
  <meta name="description" content="{excerpt}" />
  <meta property="og:type"        content="article" />
  <meta property="og:title"       content="{title} — Dana Enache" />
  <meta property="og:description" content="{excerpt}" />
  <meta property="og:url"         content="https://danaenache.com/stories/{slug}/" />
{og_image_html}  <link rel="canonical" href="https://danaenache.com/stories/{slug}/" />
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../../style.css" />
  <script>(function(){{var t=localStorage.getItem('de-theme')||'dark';document.documentElement.dataset.theme=t;}})()</script>
</head>
<body>

  <nav class="site-nav">
    <div class="nav-inner">
      <a href="../../" class="nav-logo">Dana Enache</a>
      <div class="nav-links">
        <a href="../../" class="nav-link">Home</a>
        <a href="../../books/" class="nav-link">Books</a>
        <a href="../../stories.html" class="nav-link active">Stories</a>
        <a href="../../about.html" class="nav-link">About</a>
      </div>
      <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme"></button>
    </div>
  </nav>

  <article class="story-page">
    <div class="story-page-inner">
      <header class="story-page-header">
        <a href="../../stories.html" class="back-link">← All Stories</a>
        <h1 class="story-page-title">{title}</h1>
        <div class="story-page-meta">
          <span class="badge badge-{lang}">{lang_upper}</span>
          {date_html}
        </div>
      </header>
{cover_html}      <div class="story-page-body">
{body_html}
      </div>
    </div>
  </article>

  <footer class="site-footer">
    <p>&copy; <span id="footerYear"></span> Dana Enache &mdash; All rights reserved.</p>
    <p style="margin-top:0.5rem"><a href="../../stories.html" style="color:var(--accent-hover)">← Back to all stories</a></p>
  </footer>

  <section class="story-comments">
    <div class="story-page-inner">
      <h2 class="story-comments-title">Comments</h2>
      <div id="cusdis_thread"
        data-host="https://cusdis.com"
        data-app-id="a1ee7fcb-16af-4e06-83f0-50025f921bbf"
        data-page-id="{slug}"
        data-page-url="https://danaenache.com/stories/{slug}/"
        data-page-title="{title}"
      ></div>
      <script async defer src="https://cusdis.com/js/cusdis.es.js"></script>
    </div>
  </section>

  <script src="../../theme.js"></script>
  <script>document.getElementById('footerYear').textContent = new Date().getFullYear();</script>
  <script src="../../blood.js"></script>
</body>
</html>
"""

def detect_lang(slug, text):
    if slug in KNOWN_RO_SLUGS:
        return 'ro'
    if any(c in text for c in RO_DIACRITICS):
        return 'ro'
    return 'en'

def title_from_slug(slug):
    if slug in SPECIAL_TITLES:
        return SPECIAL_TITLES[slug]
    return slug.replace('-', ' ').title()

def _linkify_escape_line(line):
    """HTML-escape a line of text, converting bare URLs to clickable links."""
    parts = URL_RE.split(line)
    out = ''
    for i, part in enumerate(parts):
        if i % 2 == 1:  # URL capture group
            url = part.rstrip('.,;:!?)\'"')
            suffix = part[len(url):]
            eu = html.escape(url)
            out += f'<a href="{eu}" target="_blank" rel="noopener noreferrer">{eu}</a>'
            out += html.escape(suffix)
        else:
            out += html.escape(part)
    return out

def text_to_html(text):
    """Convert plain text paragraphs to HTML <p> tags with clickable URLs."""
    paragraphs = text.strip().split('\n\n')
    lines = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        inner = '<br />\n'.join(_linkify_escape_line(l) for l in para.split('\n'))
        lines.append(f'        <p>{inner}</p>')
    return '\n'.join(lines)

def main():
    if os.path.exists(DATES_FILE):
        with open(DATES_FILE, encoding='utf-8') as f:
            story_dates = json.load(f)
    else:
        story_dates = {}

    today = datetime.now().strftime('%Y-%m-%d')
    stories = []

    for slug in sorted(os.listdir(STORIES_DIR)):
        story_path = os.path.join(STORIES_DIR, slug)
        if not os.path.isdir(story_path):
            continue
        story_txt = os.path.join(story_path, 'story.txt')
        if not os.path.isfile(story_txt):
            continue

        with open(story_txt, encoding='utf-8') as f:
            text = f.read().strip()

        excerpt = text[:220].replace('"', "'").replace('\n', ' ').strip()
        lang    = detect_lang(slug, text)
        title   = title_from_slug(slug)

        cover = None
        cover_filename = None
        image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        for fname in sorted(os.listdir(story_path)):
            if os.path.splitext(fname)[1].lower() in image_exts:
                cover = f'stories/{slug}/{fname}'
                cover_filename = fname
                break

        if slug not in story_dates:
            story_dates[slug] = today
        added = story_dates[slug]

        story_obj = {
            'slug':    slug,
            'title':   title,
            'lang':    lang,
            'file':    f'stories/{slug}/story.txt',
            'excerpt': excerpt,
            'added':   added,
        }
        if cover:
            story_obj['cover'] = cover
        stories.append(story_obj)

        # Generate individual story HTML page
        date_html = f'<span class="story-page-date">{added}</span>' if added else ''
        body_html = text_to_html(text)
        if cover_filename:
            og_image_html = f'  <meta property="og:image" content="https://danaenache.com/stories/{slug}/{cover_filename}" />\n'
            cover_html    = f'      <figure class="story-cover">\n        <img src="{cover_filename}" alt="{html.escape(title)}" loading="lazy" />\n      </figure>\n'
        else:
            og_image_html = ''
            cover_html    = ''
        page_html = STORY_PAGE_TEMPLATE.format(
            lang=lang,
            lang_upper=lang.upper(),
            title=html.escape(title),
            slug=slug,
            excerpt=html.escape(excerpt),
            date_html=date_html,
            body_html=body_html,
            og_image_html=og_image_html,
            cover_html=cover_html,
        )
        page_path = os.path.join(story_path, 'index.html')
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page_html)

    stories.sort(key=lambda s: s['added'], reverse=True)

    manifest = {
        'meta': {
            'generated': datetime.now().isoformat(timespec='seconds'),
            'count': len(stories),
        },
        'stories': stories,
    }
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    with open(DATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(story_dates, f, ensure_ascii=False, indent=2)

    print(f"Generated story-manifest.json with {len(stories)} stories")
    print(f"Generated {len(stories)} individual story pages (stories/{{slug}}/index.html)")

if __name__ == '__main__':
    main()
