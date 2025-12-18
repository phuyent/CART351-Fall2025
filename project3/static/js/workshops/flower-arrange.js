// Flower Arranging Workshop - Drag & Drop
let flowers = [];
let selectedFlower = null;
let vesselType = 'vase';
let flowerScale = 1;
let flowerRotation = 0;
let startTime = Date.now();

document.addEventListener('DOMContentLoaded', function() {
  setupCanvas();
  setupControls();
});

function setupCanvas() {
  const container = document.getElementById('canvasContainer');
  container.innerHTML = '<div id="flowerCanvas" style="width:100%; height:600px; position:relative; background: linear-gradient(to bottom, #f0f9ff, #e0f2fe); border-radius:12px;"></div>';
  
  // Add vessel
  const canvas = document.getElementById('flowerCanvas');
  canvas.innerHTML = '<div class="vessel" style="position:absolute; bottom:20px; left:50%; transform:translateX(-50%); font-size:8rem;">🏺</div>';
}

function setupControls() {
  // Vessel buttons
  document.querySelectorAll('.vessel-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.vessel-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      vesselType = this.dataset.vessel;
      updateVessel();
    });
  });

  // Flower library clicks
  document.querySelectorAll('.flower-item').forEach(item => {
    item.addEventListener('click', function() {
      addFlower(this.dataset.flower, this.textContent);
    });
  });

  // Scale control
  document.getElementById('flowerScale')?.addEventListener('input', function(e) {
    flowerScale = parseFloat(e.target.value);
    if (selectedFlower) updateSelectedFlower();
  });

  // Rotation control
  document.getElementById('flowerRotation')?.addEventListener('input', function(e) {
    flowerRotation = parseInt(e.target.value);
    if (selectedFlower) updateSelectedFlower();
  });

  // Delete button
  document.getElementById('deleteFlowerBtn')?.addEventListener('click', function() {
    if (selectedFlower) {
      selectedFlower.remove();
      flowers = flowers.filter(f => f !== selectedFlower);
      selectedFlower = null;
    }
  });

  // Save button
  document.getElementById('saveBtn')?.addEventListener('click', saveArrangement);
}

function addFlower(type, emoji) {
  const canvas = document.getElementById('flowerCanvas');
  const flower = document.createElement('div');
  flower.className = 'flower';
  flower.innerHTML = emoji;
  flower.style.cssText = `
    position: absolute;
    left: ${Math.random() * 60 + 20}%;
    top: ${Math.random() * 60 + 10}%;
    font-size: 4rem;
    cursor: move;
    transform: scale(1) rotate(0deg);
    transition: transform 0.3s;
  `;
  
  flower.addEventListener('click', function(e) {
    e.stopPropagation();
    selectFlower(this);
  });

  makeDraggable(flower);
  canvas.appendChild(flower);
  flowers.push(flower);
}

function makeDraggable(element) {
  let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  
  element.onmousedown = dragMouseDown;

  function dragMouseDown(e) {
    e.preventDefault();
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e.preventDefault();
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    element.style.top = (element.offsetTop - pos2) + "px";
    element.style.left = (element.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
  }
}

function selectFlower(flower) {
  document.querySelectorAll('.flower').forEach(f => f.style.border = 'none');
  flower.style.border = '3px dashed var(--primary)';
  selectedFlower = flower;
}

function updateSelectedFlower() {
  if (selectedFlower) {
    selectedFlower.style.transform = `scale(${flowerScale}) rotate(${flowerRotation}deg)`;
  }
}

function updateVessel() {
  const vessel = document.querySelector('.vessel');
  const icons = { vase: '🏺', jar: '🫙', pot: '🪴' };
  if (vessel) vessel.innerHTML = icons[vesselType] || '🏺';
}

async function saveArrangement() {
  const title = document.getElementById('arrangementTitle').value.trim();
  
  if (!title) {
    showStatus('Please enter a title!', 'error');
    return;
  }
  
  if (flowers.length === 0) {
    showStatus('Add some flowers first!', 'error');
    return;
  }

  showStatus('Saving...', 'success');

  try {
    const canvas = document.getElementById('flowerCanvas');
    const dataUrl = await htmlToImage(canvas);
    
    const response = await fetch('/api/arrangements/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workshop_type: 'flower_arranging',
        title: title,
        vessel_type: vesselType,
        image_data: dataUrl,
        flower_count: flowers.length,
        creation_time: Math.round((Date.now() - startTime) / 1000)
      })
    });

    const result = await response.json();
    if (result.status === 'success') {
      showStatus('Saved! Redirecting...', 'success');
      setTimeout(() => window.location.href = '/gallery', 2000);
    }
  } catch (error) {
    showStatus('Error: ' + error.message, 'error');
  }
}

async function htmlToImage(element) {
  // Simple screenshot using canvas
  const canvas = document.createElement('canvas');
  canvas.width = element.offsetWidth;
  canvas.height = element.offsetHeight;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#f0f9ff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/png');
}

function showStatus(message, type) {
  const el = document.getElementById('statusMessage');
  if (el) {
    el.textContent = message;
    el.className = `status-message ${type} show`;
    setTimeout(() => el.classList.remove('show'), 3000);
  }
}
// Upload button
document.getElementById('uploadFlowerBtn')?.addEventListener('click', async function() {
  const fileInput = document.getElementById('customFlowerUpload');
  const file = fileInput.files[0];
  
  if (!file) {
    showStatus('Please select an image first!', 'error');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    showStatus('Uploading...', 'success');
    
    const response = await fetch('/api/upload/flower', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showStatus('✅ Uploaded!', 'success');
      
      // Add uploaded image to library
      const library = document.getElementById('flowerLibrary');
      const item = document.createElement('div');
      item.className = 'flower-item';
      item.innerHTML = `🖼️ Custom Flower`;
      item.dataset.imageUrl = result.url;
      item.addEventListener('click', function() {
        addCustomFlower(result.url);
      });
      library.appendChild(item);
      
      fileInput.value = '';
    }
  } catch (error) {
    showStatus('Upload failed', 'error');
  }
});

// Add custom flower as image
function addCustomFlower(imageUrl) {
  const canvas = document.getElementById('flowerCanvas');
  const flower = document.createElement('img');
  flower.src = imageUrl;
  flower.className = 'flower';
  flower.style.cssText = `
    position: absolute;
    left: 50%;
    top: 50%;
    width: 80px;
    height: 80px;
    cursor: move;
    transform: translate(-50%, -50%);
  `;
  
  makeDraggable(flower);
  canvas.appendChild(flower);
  flowers.push(flower);
}

console.log('🌸 Flower Arranging Loaded');