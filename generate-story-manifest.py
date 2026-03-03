import os
import json
import html
import re
from datetime import datetime

URL_RE = re.compile(r'(https?://\S+)')

STORIES_DIR   = 'stories'
MANIFEST_FILE = 'story-manifest.json'
DATES_FILE    = 'story-dates.json'
SITEMAP_FILE  = 'sitemap.xml'
BASE_URL      = 'https://danaenache.com'

# Static pages included in every sitemap build
STATIC_PAGES = [
    {'loc': '/',                  'priority': '1.0', 'changefreq': 'weekly',  'images': [
        {'loc': '/images/books/author.jpg',      'title': 'Dana Enache, horror author'},
        {'loc': '/images/books/evolution.jpg',   'title': 'Evolution by Dana Enache'},
        {'loc': '/images/books/on-vacation.jpg', 'title': 'On Vacation by Dana Enache'},
        {'loc': '/images/books/the-dream.jpg',   'title': 'The Dream by Dana Enache'},
    ]},
    {'loc': '/about-me/',         'priority': '0.8', 'changefreq': 'monthly', 'images': [
        {'loc': '/images/books/author.jpg',      'title': 'Dana Enache, horror author'},
    ]},
    {'loc': '/books/',            'priority': '0.9', 'changefreq': 'monthly', 'images': [
        {'loc': '/images/books/evolution.jpg',   'title': 'Evolution by Dana Enache'},
        {'loc': '/images/books/on-vacation.jpg', 'title': 'On Vacation by Dana Enache'},
        {'loc': '/images/books/the-dream.jpg',   'title': 'The Dream by Dana Enache'},
    ]},
    {'loc': '/books/evolution/',  'priority': '0.8', 'changefreq': 'monthly', 'images': [
        {'loc': '/images/books/evolution.jpg',   'title': 'Evolution by Dana Enache'},
    ]},
    {'loc': '/books/on-vacation/','priority': '0.8', 'changefreq': 'monthly', 'images': [
        {'loc': '/images/books/on-vacation.jpg', 'title': 'On Vacation by Dana Enache'},
    ]},
    {'loc': '/books/the-dream/',  'priority': '0.8', 'changefreq': 'monthly', 'images': [
        {'loc': '/images/books/the-dream.jpg',   'title': 'The Dream by Dana Enache'},
    ]},
    {'loc': '/stories/',          'priority': '0.8', 'changefreq': 'weekly'},
]

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
  <meta name="keywords"    content="Dana Enache, {title}, horror story, horror short story, dark fiction, psychological horror, free horror stories, horror fiction" />
  <meta name="author"      content="Dana Enache" />
  <meta property="og:type"               content="article" />
  <meta property="og:site_name"          content="Dana Enache — Horror Author" />
  <meta property="og:title"              content="{title} — Dana Enache" />
  <meta property="og:description"        content="{excerpt}" />
  <meta property="og:url"                content="https://danaenache.com/stories/{slug}/" />
  <meta property="article:author"        content="https://danaenache.com/about-me/" />
  <meta property="article:published_time" content="{added}T00:00:00Z" />
  <meta property="article:section"       content="Horror Fiction" />
{og_image_html}  <meta name="twitter:card"        content="summary_large_image" />
  <meta name="twitter:site"        content="@danaenache_com" />
  <meta name="twitter:title"       content="{title} — Dana Enache" />
  <meta name="twitter:description" content="{excerpt}" />
{twitter_image_html}  <link rel="canonical" href="https://danaenache.com/stories/{slug}/" />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{title}",
    "name": "{title}",
    "author": {{ "@id": "https://danaenache.com/#author" }},
    "publisher": {{ "@id": "https://danaenache.com/#author" }},
    "datePublished": "{added}",
    "inLanguage": "{lang}",
    "url": "https://danaenache.com/stories/{slug}/",
    "mainEntityOfPage": "https://danaenache.com/stories/{slug}/"{article_image_json}
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home",    "item": "https://danaenache.com/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Stories", "item": "https://danaenache.com/stories/" }},
      {{ "@type": "ListItem", "position": 3, "name": "{title}" }}
    ]
  }}
  </script>
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap" media="print" onload="this.media='all'" />
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap" /></noscript>
  <link rel="stylesheet" href="../../style.min.css" />
  <script>(function(){{var t=localStorage.getItem('de-theme')||'dark';document.documentElement.dataset.theme=t;}})()</script>
</head>
<body>

  <nav class="site-nav">
    <div class="nav-inner">
      <a href="../../" class="nav-logo">Dana Enache</a>
      <div class="nav-links">
        <a href="../../" class="nav-link">Home</a>
        <a href="../../books/" class="nav-link">Books</a>
        <a href="../../stories/" class="nav-link active">Stories</a>
        <a href="../../about-me/" class="nav-link">About</a>
      </div>
      <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme"></button>
    </div>
  </nav>

  <article class="story-page">
    <div class="story-page-inner">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <ol>
          <li><a href="../../">Home</a></li>
          <li><a href="../../stories/">Stories</a></li>
          <li aria-current="page">{title}</li>
        </ol>
      </nav>
      <header class="story-page-header">
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

{next_story_html}
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
      <script>
        /* Set data-theme BEFORE cusdis.es.js loads so it picks up the right theme at init */
        (function() {{
          var t = localStorage.getItem('de-theme') || 'dark';
          document.getElementById('cusdis_thread').dataset.theme = t;
        }})();
      </script>
      <script async defer src="https://cusdis.com/js/cusdis.es.js"></script>
      <script>
        /* Auto-resize iframe to full content height — no internal scroll */
        window.addEventListener('message', function(e) {{
          if (!e.data || e.data.from !== 'cusdis') return;
          var iframe = document.querySelector('#cusdis_thread iframe');
          if (iframe && e.data.height) iframe.style.height = e.data.height + 'px';
        }});
        /* Keep theme in sync when user toggles it after load */
        new MutationObserver(function() {{
          var t = document.documentElement.dataset.theme === 'light' ? 'light' : 'dark';
          if (window.CUSDIS) window.CUSDIS.setTheme(t);
        }}).observe(document.documentElement, {{ attributes: true, attributeFilter: ['data-theme'] }});
      </script>
    </div>
  </section>

  <footer class="site-footer">
    <p>&copy; <span id="footerYear"></span> Dana Enache &mdash; All rights reserved.</p>
    <p style="margin-top:0.5rem"><a href="../../stories/" style="color:var(--accent-hover)">← Back to all stories</a></p>
  </footer>

  <script src="../../theme.min.js"></script>
  <script>document.getElementById('footerYear').textContent = new Date().getFullYear();</script>
  <script src="../../blood.min.js"></script>
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

def make_next_story_html(next_s):
    """Build the next-story section HTML, or empty string if none."""
    if not next_s:
        return ''
    cover_img = ''
    if next_s.get('cover'):
        cover_filename = os.path.basename(next_s['cover'])
        cover_img = f'<img src="../../stories/{next_s["slug"]}/{cover_filename}" alt="{html.escape(next_s["title"])}" />'
    excerpt = next_s['excerpt'][:120] + ('…' if len(next_s['excerpt']) > 120 else '')
    return f'''  <section class="story-next">
    <div class="story-page-inner">
      <a href="../../stories/{next_s["slug"]}/" class="story-next-card">
        {f'<div class="story-next-cover">{cover_img}</div>' if cover_img else ''}
        <div class="story-next-info">
          <span class="story-next-label">Next Story</span>
          <span class="story-next-title">{html.escape(next_s["title"])}</span>
          <span class="story-next-excerpt">{html.escape(excerpt)}</span>
        </div>
        <span class="story-next-arrow">→</span>
      </a>
    </div>
  </section>

'''

def write_sitemap(stories):
    """Generate sitemap.xml with static pages + all story pages."""
    def url_block(loc, priority, changefreq, lastmod=None, images=None):
        lines = [
            '  <url>',
            f'    <loc>{BASE_URL}{loc}</loc>',
        ]
        if lastmod:
            lines.append(f'    <lastmod>{lastmod}</lastmod>')
        lines += [
            f'    <changefreq>{changefreq}</changefreq>',
            f'    <priority>{priority}</priority>',
        ]
        for img in (images or []):
            lines += [
                '    <image:image>',
                f'      <image:loc>{BASE_URL}{img["loc"]}</image:loc>',
                f'      <image:title>{html.escape(img["title"])}</image:title>',
                '    </image:image>',
            ]
        lines.append('  </url>')
        return lines

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for page in STATIC_PAGES:
        out += url_block(page['loc'], page['priority'], page['changefreq'],
                         images=page.get('images'))
    for s in stories:
        images = []
        if s.get('cover'):
            cover_filename = os.path.basename(s['cover'])
            images = [{'loc': f'/stories/{s["slug"]}/{cover_filename}', 'title': s['title']}]
        out += url_block(f'/stories/{s["slug"]}/', '0.6', 'yearly',
                         lastmod=s['added'], images=images)
    out.append('</urlset>')

    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print(f"Generated {SITEMAP_FILE} ({len(STATIC_PAGES) + len(stories)} URLs)")


def main():
    if os.path.exists(DATES_FILE):
        with open(DATES_FILE, encoding='utf-8') as f:
            story_dates = json.load(f)
    else:
        story_dates = {}

    today = datetime.now().strftime('%Y-%m-%d')

    # ── Pass 1: collect all story data ──────────────────────────
    raw_stories = []
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

        raw_stories.append({
            'slug':           slug,
            'title':          title,
            'lang':           lang,
            'file':           f'stories/{slug}/story.txt',
            'excerpt':        excerpt,
            'added':          added,
            'cover':          cover,
            'cover_filename': cover_filename,
            'text':           text,
        })

    # ── Sort newest-first (same order as manifest) ───────────────
    raw_stories.sort(key=lambda s: s['added'], reverse=True)

    # ── Pass 2: generate pages with next-story context ───────────
    stories = []
    for i, s in enumerate(raw_stories):
        slug           = s['slug']
        title          = s['title']
        lang           = s['lang']
        added          = s['added']
        cover          = s['cover']
        cover_filename = s['cover_filename']
        text           = s['text']
        excerpt        = s['excerpt']

        # next = older story (one step further in newest-first list)
        next_s = raw_stories[i + 1] if i + 1 < len(raw_stories) else None

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
            og_image_html       = f'  <meta property="og:image" content="https://danaenache.com/stories/{slug}/{cover_filename}" />\n'
            twitter_image_html  = f'  <meta name="twitter:image" content="https://danaenache.com/stories/{slug}/{cover_filename}" />\n'
            article_image_json  = f',\n    "image": "https://danaenache.com/stories/{slug}/{cover_filename}"'
            cover_html          = f'      <figure class="story-cover">\n        <img src="{cover_filename}" alt="{html.escape(title)}" loading="lazy" />\n      </figure>\n'
        else:
            og_image_html      = ''
            twitter_image_html = ''
            article_image_json = ''
            cover_html         = ''

        next_story_html = make_next_story_html(next_s)

        page_html = STORY_PAGE_TEMPLATE.format(
            lang=lang,
            lang_upper=lang.upper(),
            title=html.escape(title),
            slug=slug,
            excerpt=html.escape(excerpt),
            added=added,
            date_html=date_html,
            body_html=body_html,
            og_image_html=og_image_html,
            twitter_image_html=twitter_image_html,
            article_image_json=article_image_json,
            cover_html=cover_html,
            next_story_html=next_story_html,
        )
        story_path = os.path.join(STORIES_DIR, slug)
        page_path  = os.path.join(story_path, 'index.html')
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page_html)

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

    write_sitemap(stories)

    print(f"Generated story-manifest.json with {len(stories)} stories")
    print(f"Generated {len(stories)} individual story pages (stories/{{slug}}/index.html)")

if __name__ == '__main__':
    main()
