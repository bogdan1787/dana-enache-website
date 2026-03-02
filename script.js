/**
 * script.js — Stories listing page for Dana Enache's website
 */

let allStories  = [];
let currentLang = 'all';

const storiesGrid = document.getElementById('storiesGrid');
const emptyState  = document.getElementById('emptyState');
const filterBtns  = document.querySelectorAll('.filter-btn');

async function loadManifest() {
  try {
    const res = await fetch('story-manifest.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error();
    return await res.json();
  } catch { return null; }
}

function renderStories(stories) {
  storiesGrid.innerHTML = '';
  const filtered = currentLang === 'all' ? stories : stories.filter(s => s.lang === currentLang);

  if (!filtered.length) { emptyState.classList.remove('hidden'); return; }
  emptyState.classList.add('hidden');

  filtered.forEach(story => {
    const dateStr = story.added
      ? new Date(story.added).toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' })
      : '';

    const card = document.createElement('a');
    card.className = 'story-card';
    card.href      = `stories/${story.slug}/`;

    card.innerHTML = `
      <div class="story-card-body">
        <div class="story-meta">
          <span class="badge badge-${story.lang}">${story.lang.toUpperCase()}</span>
          ${dateStr ? `<span class="story-date">${dateStr}</span>` : ''}
        </div>
        <h3 class="story-title">${story.title}</h3>
        <p class="story-excerpt">${story.excerpt || ''}</p>
        <span class="story-read-link">Read story →</span>
      </div>`;

    storiesGrid.appendChild(card);
  });
}

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentLang = btn.dataset.lang;
    renderStories(allStories);
  });
});

(async () => {
  const manifest = await loadManifest();
  if (!manifest?.stories?.length) { emptyState.classList.remove('hidden'); return; }
  allStories = manifest.stories;
  renderStories(allStories);
})();

