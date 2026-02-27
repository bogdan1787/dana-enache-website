/**
 * script.js — Portfolio gallery logic
 *
 * ┌─ Quick configuration ──────────────────────────────────────────────────┐
 * │  Open index.html and edit the <h1> and <p> tags in the <header>       │
 * │  to change the artist name and tagline.                                │
 * └────────────────────────────────────────────────────────────────────────┘
 */

// ── State ────────────────────────────────────────────────────────────────────

let allImages    = [];   // flat list: { file, alt, category (slug) }
let filteredImages = []; // current view
let lightboxIndex  = 0;  // index in filteredImages

// ── DOM refs ──────────────────────────────────────────────────────────────────

const gallery    = document.getElementById('gallery');
const catNavInner = document.querySelector('.cat-nav-inner');
const emptyState = document.getElementById('emptyState');
const lightbox   = document.getElementById('lightbox');
const lbImg      = document.getElementById('lbImg');
const lbCaption  = document.getElementById('lbCaption');
const lbClose    = document.getElementById('lbClose');
const lbPrev     = document.getElementById('lbPrev');
const lbNext     = document.getElementById('lbNext');

// ── Load manifest ─────────────────────────────────────────────────────────────

async function loadManifest() {
  try {
    const res = await fetch('image-manifest.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error('not found');
    const manifest = await res.json();
    return manifest.categories || [];
  } catch {
    return [];
  }
}

// ── Build gallery ─────────────────────────────────────────────────────────────

function buildGallery(categories) {
  if (!categories.length || !categories.some(c => c.images.length)) {
    emptyState.classList.remove('hidden');
    document.getElementById('catNav').classList.add('hidden');
    return;
  }

  // Flatten all images with category metadata
  allImages = [];
  categories.forEach(cat => {
    cat.images.forEach(img => {
      allImages.push({ file: img.file, alt: img.alt, category: cat.slug, categoryName: cat.name });
    });
  });

  // Inject category nav buttons
  categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'cat-btn';
    btn.dataset.slug = cat.slug;
    btn.textContent = cat.name;
    catNavInner.appendChild(btn);
  });

  // Default: show all
  showCategory('all', categories);
}

function showCategory(slug, categories) {
  gallery.innerHTML = '';

  if (slug === 'all') {
    // Group by category with headings
    filteredImages = [];
    categories.forEach(cat => {
      if (!cat.images.length) return;

      const heading = document.createElement('div');
      heading.className = 'category-heading';
      heading.innerHTML = `<h2>${cat.name}</h2>`;
      gallery.appendChild(heading);

      cat.images.forEach(img => {
        const idx = filteredImages.length;
        filteredImages.push({ file: img.file, alt: img.alt, category: cat.slug, categoryName: cat.name });
        gallery.appendChild(makeItem(img, idx));
      });
    });
  } else {
    filteredImages = allImages.filter(img => img.category === slug);
    filteredImages.forEach((img, idx) => gallery.appendChild(makeItem(img, idx)));
  }
}

function makeItem(img, idx) {
  const div = document.createElement('div');
  div.className = 'gallery-item';
  div.setAttribute('role', 'button');
  div.setAttribute('tabindex', '0');
  div.setAttribute('aria-label', img.alt || img.file);
  div.dataset.index = idx;

  const image = document.createElement('img');
  image.src      = img.file;
  image.alt      = img.alt || '';
  image.loading  = 'lazy';
  image.decoding = 'async';
  image.draggable = false;

  const caption = document.createElement('span');
  caption.className = 'item-caption';
  caption.textContent = img.alt;

  div.appendChild(image);
  div.appendChild(caption);

  div.addEventListener('click', () => openLightbox(idx));
  div.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openLightbox(idx); });

  return div;
}

// ── Category filter ───────────────────────────────────────────────────────────

let currentCategories = [];

catNavInner.addEventListener('click', e => {
  const btn = e.target.closest('.cat-btn');
  if (!btn) return;

  catNavInner.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  showCategory(btn.dataset.slug, currentCategories);
});

// ── Lightbox ──────────────────────────────────────────────────────────────────

function openLightbox(index) {
  lightboxIndex = index;
  renderLightbox();
  lightbox.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  lbClose.focus();
}

function closeLightbox() {
  lightbox.classList.add('hidden');
  document.body.style.overflow = '';
}

function renderLightbox() {
  const img = filteredImages[lightboxIndex];
  lbImg.src = img.file;
  lbImg.alt = img.alt;

  // Restart animation
  lbImg.style.animation = 'none';
  lbImg.offsetHeight; // reflow
  lbImg.style.animation = '';

  lbCaption.textContent = img.alt
    ? `${img.alt}  ·  ${img.categoryName}`
    : img.categoryName;

  lbPrev.style.visibility = lightboxIndex > 0                      ? 'visible' : 'hidden';
  lbNext.style.visibility = lightboxIndex < filteredImages.length - 1 ? 'visible' : 'hidden';
}

function stepLightbox(dir) {
  const next = lightboxIndex + dir;
  if (next >= 0 && next < filteredImages.length) {
    lightboxIndex = next;
    renderLightbox();
  }
}

lbClose.addEventListener('click', closeLightbox);
lbPrev.addEventListener('click',  () => stepLightbox(-1));
lbNext.addEventListener('click',  () => stepLightbox(+1));

// Click backdrop to close
lightbox.addEventListener('click', e => {
  if (e.target === lightbox) closeLightbox();
});

// Keyboard navigation
document.addEventListener('keydown', e => {
  if (lightbox.classList.contains('hidden')) return;
  if (e.key === 'Escape')      closeLightbox();
  if (e.key === 'ArrowLeft')   stepLightbox(-1);
  if (e.key === 'ArrowRight')  stepLightbox(+1);
});

// Touch swipe support (lightbox)
let touchStartX = 0;
lightbox.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
lightbox.addEventListener('touchend',   e => {
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) > 50) stepLightbox(dx < 0 ? +1 : -1);
});

// ── Image protection ─────────────────────────────────────────────────────────

// Disable right-click save on images
document.addEventListener('contextmenu', e => {
  if (e.target.tagName === 'IMG') e.preventDefault();
});

// Disable drag-to-desktop
document.addEventListener('dragstart', e => {
  if (e.target.tagName === 'IMG') e.preventDefault();
});

// ── Init ──────────────────────────────────────────────────────────────────────

(async () => {
  const categories = await loadManifest();
  currentCategories = categories;
  buildGallery(categories);
})();
