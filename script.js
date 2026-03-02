/**
 * script.js — Stories page logic for Dana Enache's website
 */

// ── State ─────────────────────────────────────────────────────────────────────
let allStories = [];
let currentLang = 'all';

// ── DOM refs ──────────────────────────────────────────────────────────────────
const storiesGrid  = document.getElementById('storiesGrid');
const emptyState   = document.getElementById('emptyState');
const storyModal   = document.getElementById('storyModal');
const modalOverlay = document.getElementById('modalOverlay');
const modalClose   = document.getElementById('modalClose');
const modalTitle   = document.getElementById('modalTitle');
const modalDate    = document.getElementById('modalDate');
const modalBody    = document.getElementById('modalBody');
const modalCoverWrap = document.getElementById('modalCoverWrap');
const filterBtns   = document.querySelectorAll('.filter-btn');

// ── Load manifest ─────────────────────────────────────────────────────────────
async function loadManifest() {
  try {
    const res = await fetch('story-manifest.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error('not found');
    return await res.json();
  } catch {
    return null;
  }
}

// ── Render stories ────────────────────────────────────────────────────────────
function renderStories(stories) {
  storiesGrid.innerHTML = '';
  const filtered = currentLang === 'all' ? stories : stories.filter(s => s.lang === currentLang);

  if (!filtered.length) {
    emptyState.classList.remove('hidden');
    return;
  }
  emptyState.classList.add('hidden');

  filtered.forEach(story => {
    const card = document.createElement('article');
    card.className = 'story-card';
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-label', `Read ${story.title}`);

    const coverHtml = story.cover
      ? `<div class="story-card-cover"><img src="${story.cover}" alt="${story.title}" loading="lazy" /></div>`
      : `<div class="story-card-cover story-card-cover--placeholder"><span class="story-skull">💀</span></div>`;

    const dateStr = story.added ? new Date(story.added).toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' }) : '';

    card.innerHTML = `
      ${coverHtml}
      <div class="story-card-body">
        <div class="story-card-meta">
          <span class="story-lang-badge">${story.lang === 'ro' ? 'RO' : 'EN'}</span>
          ${dateStr ? `<span class="story-date">${dateStr}</span>` : ''}
        </div>
        <h3 class="story-card-title">${story.title}</h3>
        <p class="story-card-excerpt">${story.excerpt || ''}</p>
        <span class="story-read-link">Read story →</span>
      </div>`;

    card.addEventListener('click', () => openStory(story));
    card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openStory(story); });
    storiesGrid.appendChild(card);
  });
}

// ── Story reader modal ────────────────────────────────────────────────────────
async function openStory(story) {
  modalTitle.textContent = story.title;
  modalDate.textContent  = story.added ? new Date(story.added).toLocaleDateString('en-GB', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
  modalBody.innerHTML    = '<p class="modal-loading">Loading story…</p>';

  // Cover
  if (story.cover) {
    modalCoverWrap.innerHTML = `<img class="modal-cover" src="${story.cover}" alt="${story.title}" />`;
  } else {
    modalCoverWrap.innerHTML = '';
  }

  storyModal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  modalClose.focus();

  // Fetch story text
  try {
    const res = await fetch(story.file);
    if (!res.ok) throw new Error('fetch failed');
    const text = await res.text();
    // Convert plain text paragraphs to HTML
    const html = text.trim()
      .split(/\n\n+/)
      .map(para => `<p>${para.replace(/\n/g, '<br>')}</p>`)
      .join('\n');
    modalBody.innerHTML = html;
  } catch {
    modalBody.innerHTML = '<p class="modal-error">Could not load story. Please try again.</p>';
  }
}

function closeStory() {
  storyModal.classList.add('hidden');
  document.body.style.overflow = '';
}

// ── Filter ────────────────────────────────────────────────────────────────────
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentLang = btn.dataset.lang;
    renderStories(allStories);
  });
});

// ── Modal close ───────────────────────────────────────────────────────────────
modalClose.addEventListener('click', closeStory);
modalOverlay.addEventListener('click', closeStory);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !storyModal.classList.contains('hidden')) closeStory();
});

// ── Image/text protection ─────────────────────────────────────────────────────
document.addEventListener('contextmenu', e => { if (e.target.tagName === 'IMG') e.preventDefault(); });

// ── Init ──────────────────────────────────────────────────────────────────────
(async () => {
  const manifest = await loadManifest();
  if (!manifest || !manifest.stories || !manifest.stories.length) {
    emptyState.classList.remove('hidden');
    return;
  }
  allStories = manifest.stories;
  renderStories(allStories);
})();

