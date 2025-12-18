// Charm Bracelet Workshop - SVG Builder
let charms = [];
let bandType = 'chain';
let bandColor = '#C0C0C0';
let charmSpacing = 60;
let startTime = Date.now();

document.addEventListener('DOMContentLoaded', function() {
  setupBracelet();
  setupControls();
});

function setupBracelet() {
  drawBracelet();
}

function setupControls() {
  // Band buttons
  document.querySelectorAll('.band-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.band-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      bandType = this.dataset.band;
      drawBracelet();
    });
  });

  // Charm library
  document.querySelectorAll('.charm-item').forEach(item => {
    item.addEventListener('click', function() {
      addCharm(this.textContent);
    });
  });

  // Spacing control
  document.getElementById('charmSpacing')?.addEventListener('input', function(e) {
    charmSpacing = parseInt(e.target.value);
    drawBracelet();
  });

  // Band color
  document.getElementById('bandColor')?.addEventListener('input', function(e) {
    bandColor = e.target.value;
    drawBracelet();
  });

  // Clear button
  document.getElementById('clearBraceletBtn')?.addEventListener('click', function() {
    if (confirm('Clear all charms?')) {
      charms = [];
      drawBracelet();
    }
  });

  // Save button
  document.getElementById('saveBtn')?.addEventListener('click', saveBracelet);
}

function addCharm(emoji) {
  if (charms.length < 12) {
    charms.push(emoji);
    drawBracelet();
  } else {
    showStatus('Maximum 12 charms!', 'error');
  }
}

function drawBracelet() {
  const svg = document.getElementById('braceletSVG');
  svg.innerHTML = '';
  
  const width = 800;
  const height = 400;
  const centerY = height / 2;
  
  // Draw band (curved line)
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  const startX = 100;
  const endX = width - 100;
  const curveDepth = 80;
  
  path.setAttribute('d', `M ${startX} ${centerY} Q ${width/2} ${centerY + curveDepth} ${endX} ${centerY}`);
  path.setAttribute('stroke', bandColor);
  path.setAttribute('stroke-width', bandType === 'leather' ? '12' : '6');
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke-linecap', 'round');
  svg.appendChild(path);

  // Draw charms along the path
  if (charms.length > 0) {
    const totalWidth = endX - startX;
    const spacing = totalWidth / (charms.length + 1);
    
    charms.forEach((charm, index) => {
      const x = startX + spacing * (index + 1);
      const t = (x - startX) / totalWidth;
      const y = centerY + curveDepth * 4 * t * (1 - t);
      
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', x);
      text.setAttribute('y', y + 10);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('font-size', '32');
      text.setAttribute('cursor', 'pointer');
      text.textContent = charm;
      
      text.addEventListener('click', function() {
        charms.splice(index, 1);
        drawBracelet();
      });
      
      svg.appendChild(text);
    });
  }
}

async function saveBracelet() {
  const title = document.getElementById('braceletTitle').value.trim();
  
  if (!title) {
    showStatus('Please enter a title!', 'error');
    return;
  }
  
  if (charms.length === 0) {
    showStatus('Add some charms first!', 'error');
    return;
  }

  showStatus('Saving...', 'success');

  try {
    const svg = document.getElementById('braceletSVG');
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 400;
    const ctx = canvas.getContext('2d');
    
    const img = new Image();
    img.onload = async function() {
      ctx.drawImage(img, 0, 0);
      const imageData = canvas.toDataURL('image/png');
      
      const response = await fetch('/api/bracelets/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workshop_type: 'charm_bracelet',
          title: title,
          band_type: bandType,
          image_data: imageData,
          charm_count: charms.length,
          creation_time: Math.round((Date.now() - startTime) / 1000)
        })
      });

      const result = await response.json();
      if (result.status === 'success') {
        showStatus('Saved! Redirecting...', 'success');
        setTimeout(() => window.location.href = '/gallery', 2000);
      }
    };
    
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
  } catch (error) {
    showStatus('Error: ' + error.message, 'error');
  }
}

function showStatus(message, type) {
  const el = document.getElementById('statusMessage');
  if (el) {
    el.textContent = message;
    el.className = `status-message ${type} show`;
    setTimeout(() => el.classList.remove('show'), 3000);
  }
}

console.log('✨ Charm Bracelet Loaded');