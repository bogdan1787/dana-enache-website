import os
import json
from datetime import datetime

# Constants
STORIES_DIR = 'stories'
MANIFEST_FILE = 'story-manifest.json'
DATES_FILE = 'story-dates.json'
KNOWN_RO_SLUGS = {
    'naluca', 'constanta', 'omul-verde', 'copilul-din-vis', 'oameni-cu-fete-monotone', '3'
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

def main():
    # Load or create story-dates.json
    if os.path.exists(DATES_FILE):
        with open(DATES_FILE, encoding='utf-8') as f:
            story_dates = json.load(f)
    else:
        story_dates = {}
    today = datetime.now().strftime('%Y-%m-%d')
    stories = []
    for slug in os.listdir(STORIES_DIR):
        story_path = os.path.join(STORIES_DIR, slug)
        if not os.path.isdir(story_path):
            continue
        story_txt = os.path.join(story_path, 'story.txt')
        if not os.path.isfile(story_txt):
            continue
        with open(story_txt, encoding='utf-8') as f:
            text = f.read().strip()
        excerpt = text[:250].strip()
        lang = detect_lang(slug, text)
        title = title_from_slug(slug)
        cover = None
        for ext in ['jpg', 'png']:
            cover_path = os.path.join(story_path, f'cover.{ext}')
            if os.path.isfile(cover_path):
                cover = f'stories/{slug}/cover.{ext}'
                break
        if slug not in story_dates:
            story_dates[slug] = today
        story_obj = {
            'slug': slug,
            'title': title,
            'lang': lang,
            'file': f'stories/{slug}/story.txt',
            'excerpt': excerpt,
            'added': story_dates[slug]
        }
        if cover:
            story_obj['cover'] = cover
        stories.append(story_obj)
    # Sort by date descending
    stories.sort(key=lambda s: s['added'], reverse=True)
    manifest = {
        'meta': {
            'generated': datetime.now().isoformat(timespec='seconds'),
            'count': len(stories)
        },
        'stories': stories
    }
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    with open(DATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(story_dates, f, ensure_ascii=False, indent=2)
    print(f"Generated story-manifest.json with {len(stories)} stories")

if __name__ == '__main__':
    main()
