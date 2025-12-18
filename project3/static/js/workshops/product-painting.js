// Product Painting Workshop - Complete Implementation
// Uses p5.js for canvas drawing

let sketchInstance;
let productType = 'mug';
let currentColor = '#FF6B6B';
let brushSize = 10;
let isEraser = false;
let strokeCount = 0;
let startTime = Date.now();
let colorTracker = new Set(['#FF6B6B']);

function setupProductPainting() {
  const sketch = (p) => {
    p.setup = function() {
      const container = document.getElementById('canvasContainer');
      const width = Math.min(800, container.clientWidth - 40);
      const height = Math.min(600, container.clientHeight - 40);
      
      const canvas = p.createCanvas(width, height);
      p.background(255);
      p.strokeCap(p.ROUND);
      p.strokeJoin(p.ROUND);
    };

    p.mouseDragged = function() {
      if (p.mouseX >= 0 && p.mouseX <= p.width && p.mouseY >= 0 && p.mouseY <= p.height) {
        p.stroke(isEraser ? 255 : currentColor);
        p.strokeWeight(brushSize);
        p.line(p.pmouseX, p.pmouseY, p.mouseX, p.mouseY);
        strokeCount++;
      }
      return false;
    };

    p.touchMoved = function() {
      if (p.mouseX >= 0 && p.mouseX <= p.width && p.mouseY >= 0 && p.mouseY <= p.height) {
        p.stroke(isEraser ? 255 : currentColor);
        p.strokeWeight(brushSize);
        p.line(p.pmouseX, p.pmouseY, p.mouseX, p.mouseY);
        strokeCount++;
      }
      return false;
    };
  };

  sketchInstance = new p5(sketch, 'canvasContainer');
}

// Product buttons
document.querySelectorAll('.product-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.product-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    productType = this.dataset.product;
  });
});

// Color buttons
document.querySelectorAll('.color-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    currentColor = this.dataset.color;
    colorTracker.add(currentColor);
    isEraser = false;
    document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
  });
});

// Custom color
document.getElementById('customColor')?.addEventListener('input', function(e) {
  currentColor = e.target.value;
  colorTracker.add(currentColor);
  isEraser = false;
  document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
});

// Brush size
document.getElementById('brushSize')?.addEventListener('input', function(e) {
  brushSize = parseInt(e.target.value);
  document.getElementById('brushSizeValue').textContent = brushSize + 'px';
});

// Eraser
document.getElementById('eraserBtn')?.addEventListener('click', function() {
  isEraser = !isEraser;
  this.style.background = isEraser ? 'var(--primaryLight)' : '';
  this.style.borderColor = isEraser ? 'var(--primary)' : '';
});

// Clear
document.getElementById('clearBtn')?.addEventListener('click', function() {
  if (confirm('Clear canvas? This cannot be undone.')) {
    sketchInstance?.clear();
    sketchInstance?.background(255);
    strokeCount = 0;
  }
});

// Save
document.getElementById('saveBtn')?.addEventListener('click', async function() {
  const title = document.getElementById('paintingTitle').value.trim();
  
  if (!title) {
    showStatus('Please enter a title!', 'error');
    return;
  }
  
  if (strokeCount === 0) {
    showStatus('Please paint something first!', 'error');
    return;
  }

  showStatus('Saving...', 'success');

  try {
    const imageData = sketchInstance.canvas.toDataURL('image/png');
    const response = await fetch('/api/paintings/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workshop_type: 'product_painting',
        title: title,
        product_type: productType,
        image_data: imageData,
        colors_used: Array.from(colorTracker),
        strokes: strokeCount,
        creation_time: Math.round((Date.now() - startTime) / 1000)
      })
    });

    const result = await response.json();
    if (result.status === 'success') {
      showStatus('Saved! Redirecting...', 'success');
      setTimeout(() => window.location.href = '/gallery', 2000);
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    showStatus('Error: ' + error.message, 'error');
  }
});

function showStatus(message, type) {
  const el = document.getElementById('statusMessage');
  if (el) {
    el.textContent = message;
    el.className = `status-message ${type} show`;
    setTimeout(() => el.classList.remove('show'), 3000);
  }
}

document.addEventListener('DOMContentLoaded', setupProductPainting);
console.log('🎨 Product Painting Loaded');