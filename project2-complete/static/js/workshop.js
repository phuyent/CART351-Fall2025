// ==========================================
// WORKSHOP CANVAS SCRIPT - p5.js Drawing Application
// ==========================================

// Global Variables
let p5Instance;
let currentColor = '#000000';
let currentBrushSize = 5;
let isEraser = false;
let strokes = 0;
let colorsUsed = new Set(['#000000']);
let startTime = Date.now();
let canvasWidth = 600;
let canvasHeight = 400;
let isDrawing = false;

// P5.js Sketch
const sketch = (p) => {
  p.setup = function() {
    const canvas = p.createCanvas(canvasWidth, canvasHeight);
    canvas.parent('canvasContainer');
    p.background(255);
    p.strokeCap(p.ROUND);
    p.strokeJoin(p.ROUND);
    
    // CRITICAL: Prevent p5 from disabling inputs
    // Remove pointer-events: none that p5 might add
    const allInputs = document.querySelectorAll('input[type="text"]');
    allInputs.forEach(input => {
      input.style.pointerEvents = '';  // Clear any p5 override
    });
  };

  p.draw = function() {
    // Drawing happens in mouseDragged
  };

  p.mouseDragged = function() {
    if (p.mouseX >= 0 && p.mouseX <= p.width && p.mouseY >= 0 && p.mouseY <= p.height) {
      if (!isDrawing) {
        isDrawing = true;
        strokes++;
        updateStats();
      }

      if (isEraser) {
        p.stroke(255);
        p.strokeWeight(currentBrushSize * 2);
      } else {
        p.stroke(currentColor);
        p.strokeWeight(currentBrushSize);
      }

      p.line(p.pmouseX, p.pmouseY, p.mouseX, p.mouseY);
    }
    return false;
  };

  p.mouseReleased = function() {
    isDrawing = false;
  };

  p.touchStarted = function() {
    return false; // Prevent default touch behavior
  };

  p.touchMoved = function() {
    if (p.mouseX >= 0 && p.mouseX <= p.width && p.mouseY >= 0 && p.mouseY <= p.height) {
      if (!isDrawing) {
        isDrawing = true;
        strokes++;
        updateStats();
      }

      if (isEraser) {
        p.stroke(255);
        p.strokeWeight(currentBrushSize * 2);
      } else {
        p.stroke(currentColor);
        p.strokeWeight(currentBrushSize);
      }

      p.line(p.pmouseX, p.pmouseY, p.mouseX, p.mouseY);
    }
    return false;
  };

  p.touchEnded = function() {
    isDrawing = false;
    return false;
  };
};

// Initialize p5 when page loads
window.addEventListener('DOMContentLoaded', () => {
  // Small delay to ensure all DOM elements are ready
  setTimeout(() => {
    p5Instance = new p5(sketch);
    initializeEventListeners();
    startTimer();
    console.log('✅ Workshop initialized successfully');
    
    // CRITICAL FIX: p5.js sometimes disables pointer-events globally
    // Force re-enable inputs after p5 initialization
    const forceEnableInputs = () => {
      const artistInput = document.getElementById('artistName');
      const titleInput = document.getElementById('paintingTitle');
      
      if (artistInput) {
        artistInput.style.removeProperty('pointer-events');
        artistInput.style.removeProperty('z-index');
        artistInput.disabled = false;
        artistInput.readOnly = false;
      }
      
      if (titleInput) {
        titleInput.style.removeProperty('pointer-events');
        titleInput.style.removeProperty('z-index');
        titleInput.disabled = false;
        titleInput.readOnly = false;
      }
    };
    
    // Run multiple times to ensure p5.js doesn't override
    setTimeout(forceEnableInputs, 200);
    setTimeout(forceEnableInputs, 500);
    setTimeout(forceEnableInputs, 1000);
    
    console.log('✅ Input fields force-enabled after p5 init');
  }, 100);
});

// ==========================================
// EVENT LISTENERS
// ==========================================

function initializeEventListeners() {
  // FIRST: Force enable input fields
  const artistInput = document.getElementById('artistName');
  const titleInput = document.getElementById('paintingTitle');
  
  if (artistInput) {
    artistInput.disabled = false;
    artistInput.readOnly = false;
    artistInput.style.pointerEvents = 'auto';
    artistInput.style.zIndex = '100';
    console.log('✅ Artist name input enabled');
    
    // Add click listener to auto-focus
    artistInput.addEventListener('click', () => {
      artistInput.focus();
    });
    
    // Also focus when clicking the parent form-group
    const artistFormGroup = artistInput.closest('.form-group');
    if (artistFormGroup) {
      artistFormGroup.addEventListener('click', (e) => {
        if (e.target !== artistInput) {
          artistInput.focus();
        }
      });
    }
  }
  
  if (titleInput) {
    titleInput.disabled = false;
    titleInput.readOnly = false;
    titleInput.style.pointerEvents = 'auto';
    titleInput.style.zIndex = '100';
    console.log('✅ Painting title input enabled');
    
    // Add click listener to auto-focus
    titleInput.addEventListener('click', () => {
      titleInput.focus();
    });
    
    // Also focus when clicking the parent form-group
    const titleFormGroup = titleInput.closest('.form-group');
    if (titleFormGroup) {
      titleFormGroup.addEventListener('click', (e) => {
        if (e.target !== titleInput) {
          titleInput.focus();
        }
      });
    }
  }
  
  // Canvas Size Buttons
  document.querySelectorAll('.size-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      canvasWidth = parseInt(btn.dataset.width);
      canvasHeight = parseInt(btn.dataset.height);
    });
  });

  // Apply Canvas Size
  document.getElementById('applyCanvasSize').addEventListener('click', () => {
    resizeCanvas();
  });

  // Color Palette Buttons
  document.querySelectorAll('.color-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentColor = btn.dataset.color;
      colorsUsed.add(currentColor);
      isEraser = false;
      updateStats();
      
      // Update custom color picker to match
      document.getElementById('colorPicker').value = currentColor;
    });
  });

  // Custom Color Picker
  document.getElementById('colorPicker').addEventListener('input', (e) => {
    currentColor = e.target.value;
    colorsUsed.add(currentColor);
    isEraser = false;
    updateStats();
    
    // Deactivate preset color buttons
    document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
  });

  // Brush Size Slider
  const brushSizeSlider = document.getElementById('brushSize');
  const brushSizeDisplay = document.getElementById('brushSizeDisplay');
  
  if (brushSizeSlider && brushSizeDisplay) {
    brushSizeSlider.addEventListener('input', (e) => {
      currentBrushSize = parseInt(e.target.value);
      brushSizeDisplay.textContent = `${currentBrushSize}px`;
      console.log('Brush size changed to:', currentBrushSize);
    });
    console.log('✅ Brush size slider initialized');
  } else {
    console.error('❌ Brush size elements not found');
  }

  // Eraser Button
  document.getElementById('eraserBtn').addEventListener('click', () => {
    isEraser = !isEraser;
    const btn = document.getElementById('eraserBtn');
    if (isEraser) {
      btn.style.background = 'var(--primaryBg)';
      btn.style.borderColor = 'var(--primary)';
      btn.style.color = 'var(--primaryFg)';
    } else {
      btn.style.background = '';
      btn.style.borderColor = '';
      btn.style.color = '';
    }
  });

  // Clear Canvas Button
  document.getElementById('clearBtn').addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the canvas? This cannot be undone.')) {
      clearCanvas();
    }
  });

  // Save Button
  document.getElementById('saveBtn').addEventListener('click', saveToServer);
}

// ==========================================
// CANVAS FUNCTIONS
// ==========================================

function resizeCanvas() {
  // Save current canvas content
  const currentCanvas = p5Instance.get();
  
  // Resize
  p5Instance.resizeCanvas(canvasWidth, canvasHeight);
  p5Instance.background(255);
  
  // Try to restore content (scaled)
  p5Instance.image(currentCanvas, 0, 0, canvasWidth, canvasHeight);
  
  showStatusMessage('Canvas resized successfully!', 'success');
}

function clearCanvas() {
  p5Instance.background(255);
  strokes = 0;
  colorsUsed = new Set([currentColor]);
  updateStats();
  showStatusMessage('Canvas cleared!', 'success');
}

// ==========================================
// STATS TRACKING
// ==========================================

function updateStats() {
  document.getElementById('strokeDisplay').textContent = strokes;
  document.getElementById('colorDisplay').textContent = colorsUsed.size;
}

function startTimer() {
  setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('timeDisplay').textContent = 
      `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, 1000);
}

function getTimeSpent() {
  return Math.floor((Date.now() - startTime) / 1000);
}

// ==========================================
// SAVE TO SERVER
// ==========================================

async function saveToServer() {
  const artistName = document.getElementById('artistName').value.trim();
  const paintingTitle = document.getElementById('paintingTitle').value.trim();

  // Validation
  if (!artistName) {
    showStatusMessage('Please enter your name!', 'error');
    return;
  }

  if (!paintingTitle) {
    showStatusMessage('Please enter a painting title!', 'error');
    return;
  }

  // Check if canvas is blank (mostly white)
  if (strokes === 0) {
    showStatusMessage('Please create something before saving!', 'error');
    return;
  }

  // Show saving message
  showStatusMessage('Saving your painting...', 'success');

  try {
    // Get canvas as base64 image
    const canvas = document.querySelector('#canvasContainer canvas');
    const imageData = canvas.toDataURL('image/png');

    // Prepare data in FLAT structure (not nested) to match server expectations
    const saveData = {
      artist_name: artistName,
      painting_title: paintingTitle,
      image_data: imageData,
      canvas_size: {
        width: canvasWidth,
        height: canvasHeight
      },
      colors_used: Array.from(colorsUsed),
      brush_size: currentBrushSize,
      creation_time: getTimeSpent(),
      strokes: strokes,
      timestamp: new Date().toISOString()
    };

    // Send to server
    const response = await fetch('/api/save-painting', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(saveData)
    });

    const result = await response.json();

    if (response.ok && result.status === 'success') {
      showStatusMessage('Painting saved successfully! 🎨', 'success');
      
      // Optional: Clear form or reset canvas after successful save
      setTimeout(() => {
        if (confirm('Your painting has been saved! Would you like to start a new one?')) {
          clearCanvas();
          document.getElementById('artistName').value = '';
          document.getElementById('paintingTitle').value = '';
          startTime = Date.now();
        }
      }, 2000);
    } else {
      throw new Error(result.message || 'Failed to save painting');
    }
  } catch (error) {
    console.error('Error saving painting:', error);
    showStatusMessage('Error saving painting. Please try again.', 'error');
  }
}

// ==========================================
// UI HELPERS
// ==========================================

function showStatusMessage(message, type) {
  const statusDiv = document.getElementById('statusMessage');
  statusDiv.textContent = message;
  statusDiv.className = `status-message ${type} show`;
  
  setTimeout(() => {
    statusDiv.classList.remove('show');
  }, 3000);
}

// ==========================================
// KEYBOARD SHORTCUTS (Optional Enhancement)
// ==========================================

document.addEventListener('keydown', (e) => {
  // E for eraser
  if (e.key === 'e' || e.key === 'E') {
    document.getElementById('eraserBtn').click();
  }
  
  // C for clear (with Ctrl/Cmd)
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    document.getElementById('clearBtn').click();
  }
  
  // S for save (with Ctrl/Cmd)
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    document.getElementById('saveBtn').click();
  }
  
  // Bracket keys for brush size
  if (e.key === '[') {
    const slider = document.getElementById('brushSize');
    slider.value = Math.max(1, parseInt(slider.value) - 2);
    slider.dispatchEvent(new Event('input'));
  }
  if (e.key === ']') {
    const slider = document.getElementById('brushSize');
    slider.value = Math.min(50, parseInt(slider.value) + 2);
    slider.dispatchEvent(new Event('input'));
  }
});

// ==========================================
// CONSOLE INFO (Development)
// ==========================================

console.log('%c🎨 Workshop Canvas Loaded', 'color: #ec5e95; font-size: 16px; font-weight: bold;');
console.log('%cKeyboard Shortcuts:', 'color: #50fa7b; font-weight: bold;');
console.log('  E - Toggle Eraser');
console.log('  Ctrl/Cmd + K - Clear Canvas');
console.log('  Ctrl/Cmd + S - Save Painting');
console.log('  [ / ] - Decrease/Increase Brush Size');

// ==========================================
// NUCLEAR FIX - Force inputs to work
// ==========================================

// This function aggressively ensures inputs remain functional
function nuclearInputFix() {
  const inputs = [
    document.getElementById('artistName'),
    document.getElementById('paintingTitle')
  ];
  
  inputs.forEach(input => {
    if (input) {
      // Remove any blocking styles
      input.style.pointerEvents = '';
      input.style.zIndex = '';
      
      // Ensure it's enabled
      input.disabled = false;
      input.readOnly = false;
      
      // Make sure it's visible
      input.style.opacity = '';
      input.style.visibility = '';
      
      // CRITICAL: Add mousedown listener to force focus
      // Remove old listener first to prevent duplicates
      input.removeEventListener('mousedown', forceFocusHandler);
      input.addEventListener('mousedown', forceFocusHandler);
    }
  });
}

// Handler that forces focus on mousedown
function forceFocusHandler(e) {
  e.target.focus();
}

// Run immediately
nuclearInputFix();

// Run after p5 has time to initialize
setTimeout(nuclearInputFix, 500);
setTimeout(nuclearInputFix, 1000);
setTimeout(nuclearInputFix, 2000);

// Keep checking periodically (remove in production)
setInterval(nuclearInputFix, 3000);

console.log('🔧 Nuclear input fix activated - inputs will auto-focus on click');
