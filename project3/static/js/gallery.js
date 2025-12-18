// Gallery - Load and display all creations from database
let allCreations = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', function() {
  loadGallery();
  setupFilters();
  setupModal();
});

async function loadGallery() {
  const loadingEl = document.getElementById('loadingIndicator');
  const gridEl = document.getElementById('galleryGrid');
  const noItemsEl = document.getElementById('noItems');

  try {
    loadingEl.style.display = 'flex';
    gridEl.innerHTML = '';

    const response = await fetch('/api/creations/all');
    const data = await response.json();

    loadingEl.style.display = 'none';

    if (data.status === 'success' && data.creations && data.creations.length > 0) {
      allCreations = data.creations;
      renderCreations(allCreations);
      noItemsEl.style.display = 'none';
    } else {
      noItemsEl.style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading gallery:', error);
    loadingEl.style.display = 'none';
    gridEl.innerHTML = '<p style="text-align:center;color:var(--textDim);">Error loading gallery</p>';
  }
}

function renderCreations(creations) {
  const grid = document.getElementById('galleryGrid');
  grid.innerHTML = '';

  const filtered = currentFilter === 'all' ? creations : 
    creations.filter(c => getWorkshopFilter(c.workshop_type) === currentFilter);

  filtered.forEach((creation, index) => {
    const card = createCard(creation, index);
    grid.appendChild(card);
  });

  // Animate cards
  setTimeout(() => {
    document.querySelectorAll('.gallery-item').forEach((card, i) => {
      setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, i * 50);
    });
  }, 10);
}

function createCard(creation, index) {
  const card = document.createElement('div');
  card.className = 'gallery-item';
  card.style.opacity = '0';
  card.style.transform = 'translateY(20px)';
  card.style.transition = 'all 0.5s ease';

  const workshopEmoji = {
    'product_painting': '🎨',
    'flower_arranging': '🌸',
    'charm_bracelet': '✨'
  };

  const date = new Date(creation.created_at || creation.timestamp || Date.now());
  const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  card.innerHTML = `
    <div class="gallery-item-image">
      <img src="${creation.image_data || creation.image_snapshot || ''}" alt="${creation.title || 'Creation'}">
      <div class="workshop-type-badge">
        ${workshopEmoji[creation.workshop_type] || '🎨'} 
        ${getWorkshopName(creation.workshop_type)}
      </div>
    </div>
    <div class="gallery-item-info">
      <div class="gallery-item-title">${escapeHtml(creation.title || 'Untitled')}</div>
      <div class="gallery-item-artist">by ${escapeHtml(creation.artist_name || creation.username || 'Anonymous')}</div>
      <div class="gallery-item-meta">
        <div class="gallery-item-likes">❤️ ${creation.likes || 0}</div>
        <div class="gallery-item-date">${formattedDate}</div>
      </div>
    </div>
  `;

  card.addEventListener('click', () => showModal(creation));
  return card;
}

function getWorkshopName(type) {
  const names = {
    'product_painting': 'Painting',
    'flower_arranging': 'Flowers',
    'charm_bracelet': 'Bracelet'
  };
  return names[type] || 'Creation';
}

function getWorkshopFilter(type) {
  const filters = {
    'product_painting': 'painting',
    'flower_arranging': 'flowers',
    'charm_bracelet': 'bracelets'
  };
  return filters[type] || 'all';
}

function setupFilters() {
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      currentFilter = this.dataset.filter;
      renderCreations(allCreations);
    });
  });

  document.getElementById('sortSelect')?.addEventListener('change', function(e) {
    sortCreations(e.target.value);
  });
}

function sortCreations(sortBy) {
  let sorted = [...allCreations];
  
  if (sortBy === 'newest') {
    sorted.sort((a, b) => new Date(b.created_at || b.timestamp || 0) - new Date(a.created_at || a.timestamp || 0));
  } else if (sortBy === 'likes') {
    sorted.sort((a, b) => (b.likes || 0) - (a.likes || 0));
  }
  
  allCreations = sorted;
  renderCreations(allCreations);
}

function setupModal() {
  const modal = document.getElementById('creationModal');
  const closeBtn = document.querySelector('.modal-close');

  closeBtn?.addEventListener('click', closeModal);
  modal?.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });
}

function showModal(creation) {
  const modal = document.getElementById('creationModal');
  const modalBody = document.getElementById('modalBody');

  const date = new Date(creation.created_at || creation.timestamp || Date.now());
  const formattedDate = date.toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  modalBody.innerHTML = `
    <img src="${creation.image_data || creation.image_snapshot || ''}" 
         alt="${creation.title}" 
         class="modal-creation-image">
    
    <div class="modal-creation-title">${escapeHtml(creation.title || 'Untitled')}</div>
    <div class="modal-creation-artist">by ${escapeHtml(creation.artist_name || creation.username || 'Anonymous')}</div>
    
    <div class="modal-creation-stats">
      <div class="modal-stat-item">
        <div class="modal-stat-label">Workshop</div>
        <div class="modal-stat-value">${getWorkshopName(creation.workshop_type)}</div>
      </div>
      
      <div class="modal-stat-item">
        <div class="modal-stat-label">Likes</div>
        <div class="modal-stat-value">${creation.likes || 0}</div>
      </div>
      
      <div class="modal-stat-item">
        <div class="modal-stat-label">Created</div>
        <div class="modal-stat-value">${formattedDate}</div>
      </div>
    </div>
    
    <button class="btn btn-primary modal-like-button" onclick="likeCreation('${creation._id || creation.id}')">
      ❤️ Like This Creation
    </button>
  `;

  modal.classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('creationModal');
  modal.classList.remove('show');
  document.body.style.overflow = '';
}

async function likeCreation(id) {
  try {
    const response = await fetch(`/api/creations/${id}/like`, {
      method: 'POST'
    });
    
    const result = await response.json();
    if (result.status === 'success') {
      showStatus('Liked! ❤️', 'success');
      await loadGallery();
      closeModal();
    }
  } catch (error) {
    showStatus('Error liking creation', 'error');
  }
}

function showStatus(message, type) {
  // Simple toast notification
  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed; top: 100px; right: 2rem; padding: 1rem 2rem;
    background: ${type === 'success' ? 'var(--secondaryLight)' : '#fee'};
    color: ${type === 'success' ? 'var(--secondary)' : '#c33'};
    border-radius: 12px; box-shadow: var(--shadowHover);
    z-index: 9999; font-weight: 600;
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

console.log('🖼️ Gallery Loaded');