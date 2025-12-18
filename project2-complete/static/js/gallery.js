// ==========================================
// GALLERY SCRIPT - Dynamic Painting Display
// ==========================================

// Global Variables
let allPaintings = [];
let currentModal = null;

// ==========================================
// INITIALIZATION
// ==========================================

window.addEventListener('DOMContentLoaded', async () => {
  console.log('%c🖼️ Gallery Loaded', 'color: #50fa7b; font-size: 16px; font-weight: bold;');
  
  await loadGallery();
  await loadStats();
  initializeModal();
});

// ==========================================
// FETCH AND LOAD GALLERY
// ==========================================

async function loadGallery() {
  const loadingIndicator = document.getElementById('loadingIndicator');
  const paintingsGrid = document.getElementById('paintingsGrid');
  const noPaintings = document.getElementById('noPaintings');

  try {
    // Show loading
    loadingIndicator.style.display = 'flex';
    paintingsGrid.style.display = 'none';
    noPaintings.style.display = 'none';

    // Fetch paintings from server
    const response = await fetch('/api/get-paintings');
    const data = await response.json();

    // Hide loading
    loadingIndicator.style.display = 'none';

    if (response.ok && data.paintings && data.paintings.length > 0) {
      allPaintings = data.paintings;
      renderPaintings(allPaintings);
      paintingsGrid.style.display = 'grid';
    } else {
      noPaintings.style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading gallery:', error);
    loadingIndicator.style.display = 'none';
    
    // Show error message
    paintingsGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 4rem; color: var(--textDim);">
        <p style="font-size: 1.5rem; margin-bottom: 1rem;">⚠️ Error loading paintings</p>
        <p>Please try refreshing the page</p>
      </div>
    `;
    paintingsGrid.style.display = 'grid';
  }
}

// ==========================================
// RENDER PAINTINGS GRID
// ==========================================

function renderPaintings(paintings) {
  const paintingsGrid = document.getElementById('paintingsGrid');
  paintingsGrid.innerHTML = '';

  // Sort paintings by timestamp (newest first)
  // Handle both flat and nested structures
  const sortedPaintings = [...paintings].sort((a, b) => {
    const aTime = a.timestamp || (a.metadata && a.metadata.timestamp) || 0;
    const bTime = b.timestamp || (b.metadata && b.metadata.timestamp) || 0;
    return new Date(bTime) - new Date(aTime);
  });

  sortedPaintings.forEach((painting, index) => {
    const card = createPaintingCard(painting, index);
    paintingsGrid.appendChild(card);
  });

  // Add stagger animation
  animateCards();
}

// ==========================================
// CREATE PAINTING CARD
// ==========================================

function createPaintingCard(painting, index) {
  const card = document.createElement('div');
  card.className = 'painting-card';
  card.style.opacity = '0';
  card.style.transform = 'translateY(20px)';

  // Handle both flat and nested structures
  const data = painting.metadata || painting;
  
  // Get values with fallbacks
  const title = data.painting_title || data.title || 'Untitled';
  const artistName = data.artist_name || 'Anonymous';
  const timeSpent = formatTime(data.creation_time || data.time_spent || 0);
  const colorsUsed = data.colors_used || [];
  const strokes = data.strokes || 0;
  const timestamp = data.timestamp || painting.timestamp || new Date().toISOString();
  const imageUrl = painting.image_url || painting.image_data || '';
  
  // Format date
  const date = new Date(timestamp);
  const formattedDate = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  card.innerHTML = `
    <img 
      src="${imageUrl}" 
      alt="${escapeHtml(title)}" 
      class="painting-image"
      loading="lazy"
    >
    <div class="painting-info">
      <div class="painting-title">${escapeHtml(title)}</div>
      <div class="painting-artist">by ${escapeHtml(artistName)}</div>
      <div class="painting-meta">
        <span>🕐 ${timeSpent}</span>
        <span>🎨 ${colorsUsed.length} colors</span>
      </div>
      <div class="painting-meta" style="border-top: none; padding-top: 0.5rem;">
        <span>📅 ${formattedDate}</span>
        <span>✏️ ${strokes} strokes</span>
      </div>
    </div>
  `;

  // Add click event to open modal
  card.addEventListener('click', () => {
    showModal(painting);
  });

  return card;
}

// ==========================================
// ANIMATE CARDS ON LOAD
// ==========================================

function animateCards() {
  const cards = document.querySelectorAll('.painting-card');
  
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.style.transition = 'all 0.5s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, index * 50); // Stagger by 50ms
  });
}

// ==========================================
// LOAD AND DISPLAY STATISTICS
// ==========================================

async function loadStats() {
  try {
    const response = await fetch('/api/gallery-stats');
    const data = await response.json();

    if (response.ok && data.stats) {
      displayStats(data.stats);
    }
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

function displayStats(stats) {
  // Animate numbers counting up
  animateNumber('totalPaintings', 0, stats.total_paintings, 1000);
  animateNumber('totalArtists', 0, stats.unique_artists, 1000);
  animateNumber('avgTime', 0, Math.round(stats.avg_time_spent / 60), 1000);
}

// ==========================================
// MODAL FUNCTIONALITY
// ==========================================

function initializeModal() {
  const modal = document.getElementById('paintingModal');
  const closeBtn = document.querySelector('.modal-close');

  // Close modal when clicking X
  closeBtn.addEventListener('click', () => {
    closeModal();
  });

  // Close modal when clicking outside
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // Close modal with Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('show')) {
      closeModal();
    }
  });
}

function showModal(painting) {
  const modal = document.getElementById('paintingModal');
  const modalBody = document.getElementById('modalBody');
  
  currentModal = painting;

  // Handle both flat and nested structures
  const data = painting.metadata || painting;
  
  // Get values with fallbacks
  const title = data.painting_title || data.title || 'Untitled';
  const artistName = data.artist_name || 'Anonymous';
  const timeSpent = formatTime(data.creation_time || data.time_spent || 0);
  const colorsUsed = data.colors_used || [];
  const strokes = data.strokes || 0;
  const timestamp = data.timestamp || painting.timestamp || new Date().toISOString();
  const imageUrl = painting.image_url || painting.image_data || '';
  const canvasSize = data.canvas_size || {};
  const canvasWidth = canvasSize.width || data.canvas_width || 800;
  const canvasHeight = canvasSize.height || data.canvas_height || 600;
  
  // Format date
  const date = new Date(timestamp);
  const formattedDate = date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  // Create color swatches
  const colorSwatches = colorsUsed
    .map(color => `
      <div style="
        width: 40px; 
        height: 40px; 
        background: ${color}; 
        border: 2px solid var(--cardBorder); 
        border-radius: 8px;
        display: inline-block;
        margin: 0 4px;
      "></div>
    `)
    .join('');

  modalBody.innerHTML = `
    <img 
      src="${imageUrl}" 
      alt="${escapeHtml(title)}" 
      class="modal-painting-image"
    >
    
    <div class="modal-painting-title">${escapeHtml(title)}</div>
    <div class="modal-painting-artist">by ${escapeHtml(artistName)}</div>
    
    <div class="modal-painting-stats">
      <div class="modal-stat-item">
        <div class="modal-stat-label">Canvas Size</div>
        <div class="modal-stat-value">${canvasWidth} × ${canvasHeight}</div>
      </div>
      
      <div class="modal-stat-item">
        <div class="modal-stat-label">Time Spent</div>
        <div class="modal-stat-value">${timeSpent}</div>
      </div>
      
      <div class="modal-stat-item">
        <div class="modal-stat-label">Total Strokes</div>
        <div class="modal-stat-value">${strokes.toLocaleString()}</div>
      </div>
      
      <div class="modal-stat-item">
        <div class="modal-stat-label">Colors Used</div>
        <div class="modal-stat-value">${colorsUsed.length}</div>
      </div>
    </div>
    
    <div style="margin-top: 2rem;">
      <div class="modal-stat-label" style="margin-bottom: 1rem;">Color Palette</div>
      <div style="text-align: center;">
        ${colorSwatches}
      </div>
    </div>
    
    <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--cardBorder);">
      <div class="modal-stat-label">Created On</div>
      <div style="color: var(--textDim); margin-top: 0.5rem;">${formattedDate}</div>
    </div>
  `;

  modal.classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('paintingModal');
  modal.classList.remove('show');
  document.body.style.overflow = '';
  currentModal = null;
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

function formatTime(seconds) {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes < 60) {
    return remainingSeconds > 0 
      ? `${minutes}m ${remainingSeconds}s` 
      : `${minutes}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  return remainingMinutes > 0 
    ? `${hours}h ${remainingMinutes}m` 
    : `${hours}h`;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function animateNumber(elementId, start, end, duration) {
  const element = document.getElementById(elementId);
  const startTime = performance.now();
  
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Easing function (ease-out)
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (end - start) * easeOut);
    
    element.textContent = current;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = end;
    }
  }
  
  requestAnimationFrame(update);
}

// ==========================================
// OPTIONAL: AUTO-REFRESH GALLERY
// ==========================================

// Uncomment to enable auto-refresh every 30 seconds
/*
setInterval(async () => {
  const currentScroll = window.scrollY;
  await loadGallery();
  await loadStats();
  window.scrollTo(0, currentScroll);
}, 30000);
*/

// ==========================================
// OPTIONAL: FILTERING & SORTING
// ==========================================

function filterPaintingsByArtist(artistName) {
  const filtered = allPaintings.filter(p => 
    p.metadata.artist_name.toLowerCase().includes(artistName.toLowerCase())
  );
  renderPaintings(filtered);
}

function sortPaintings(criteria) {
  let sorted;
  
  switch(criteria) {
    case 'newest':
      sorted = [...allPaintings].sort((a, b) => 
        new Date(b.metadata.timestamp) - new Date(a.metadata.timestamp)
      );
      break;
    case 'oldest':
      sorted = [...allPaintings].sort((a, b) => 
        new Date(a.metadata.timestamp) - new Date(b.metadata.timestamp)
      );
      break;
    case 'most-strokes':
      sorted = [...allPaintings].sort((a, b) => 
        b.metadata.strokes - a.metadata.strokes
      );
      break;
    case 'longest-time':
      sorted = [...allPaintings].sort((a, b) => 
        b.metadata.time_spent - a.metadata.time_spent
      );
      break;
    default:
      sorted = allPaintings;
  }
  
  renderPaintings(sorted);
}

// Export functions for potential use elsewhere
window.galleryFunctions = {
  filterPaintingsByArtist,
  sortPaintings,
  loadGallery,
  loadStats
};

// ==========================================
// CONSOLE INFO (Development)
// ==========================================

console.log('%cGallery Functions Available:', 'color: #50fa7b; font-weight: bold;');
console.log('  window.galleryFunctions.filterPaintingsByArtist(name)');
console.log('  window.galleryFunctions.sortPaintings(criteria)');
console.log('  window.galleryFunctions.loadGallery()');
console.log('  window.galleryFunctions.loadStats()');
