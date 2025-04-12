// Notify that content script has loaded
console.log('Screen Writer content script loaded');

class ScreenWriter {
  constructor() {
    console.log('Initializing ScreenWriter');
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'screen-writer-canvas';
    this.canvas.style.position = 'fixed';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.zIndex = '2147483647';
    this.canvas.style.pointerEvents = 'none';
    
    this.ctx = this.canvas.getContext('2d');
    this.isDrawing = false;
    this.isEnabled = false;
    this.tool = 'pen';
    this.color = '#000000';
    this.size = 5;
    this.startX = 0;
    this.startY = 0;

    document.body.appendChild(this.canvas);
    console.log('Canvas appended to body');
    this.resizeCanvas();
    this.setupEventListeners();
  }

  resizeCanvas() {
    console.log('Resizing canvas');
    const rect = document.documentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
    // Restore context properties after resize
    this.updateSettings({
      tool: this.tool,
      color: this.color,
      size: this.size
    });
  }

  setupEventListeners() {
    window.addEventListener('resize', () => {
      console.log('Window resized');
      this.resizeCanvas();
    });
    
    // Prevent context menu when drawing is enabled
    this.canvas.addEventListener('contextmenu', (e) => {
      if (this.isEnabled) {
        e.preventDefault();
      }
    });

    // Prevent text selection on the page
    document.addEventListener('selectstart', (e) => {
      if (this.isEnabled) {
        e.preventDefault();
      }
    });

    this.canvas.addEventListener('mousedown', (e) => {
      console.log('Mouse down', { enabled: this.isEnabled, x: e.clientX, y: e.clientY });
      if (!this.isEnabled) return;
      e.preventDefault();
      e.stopPropagation();
      
      this.isDrawing = true;
      this.startX = e.clientX;
      this.startY = e.clientY;
      
      if (this.tool === 'pen' || this.tool === 'eraser') {
        this.ctx.beginPath();
        this.ctx.moveTo(this.startX, this.startY);
        this.ctx.lineTo(this.startX, this.startY);
        this.ctx.stroke();
      }
    });

    this.canvas.addEventListener('mousemove', (e) => {
      if (!this.isEnabled || !this.isDrawing) return;
      e.preventDefault();
      e.stopPropagation();

      console.log('Mouse move', { x: e.clientX, y: e.clientY });

      if (this.tool === 'pen' || this.tool === 'eraser') {
        this.ctx.beginPath();
        this.ctx.moveTo(this.startX, this.startY);
        this.ctx.lineTo(e.clientX, e.clientY);
        this.ctx.stroke();
        this.startX = e.clientX;
        this.startY = e.clientY;
      } else {
        // Preview shape while dragging
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Copy existing content
        tempCtx.drawImage(this.canvas, 0, 0);
        
        // Set the same styles as main context
        tempCtx.strokeStyle = this.ctx.strokeStyle;
        tempCtx.lineWidth = this.ctx.lineWidth;
        tempCtx.lineCap = this.ctx.lineCap;
        tempCtx.lineJoin = this.ctx.lineJoin;
        
        // Draw new shape
        this.drawShape(tempCtx, this.startX, this.startY, e.clientX, e.clientY);
        
        // Clear main canvas and draw updated content
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(tempCanvas, 0, 0);
      }
    });

    const endDrawing = (e) => {
      if (!this.isEnabled || !this.isDrawing) return;
      e.preventDefault();
      e.stopPropagation();
      
      console.log('Drawing ended');
      
      if (this.tool !== 'pen' && this.tool !== 'eraser') {
        this.drawShape(this.ctx, this.startX, this.startY, e.clientX, e.clientY);
      }
      this.isDrawing = false;
    };

    this.canvas.addEventListener('mouseup', endDrawing);
    this.canvas.addEventListener('mouseleave', endDrawing);

    // Handle focus/blur events to maintain drawing state
    window.addEventListener('focus', () => {
      if (this.isEnabled) {
        document.body.classList.add('drawing-active');
      }
    });

    window.addEventListener('blur', () => {
      this.isDrawing = false;
    });
  }

  drawShape(context, startX, startY, endX, endY) {
    context.beginPath();
    
    switch (this.tool) {
      case 'square':
        const squareSize = Math.min(Math.abs(endX - startX), Math.abs(endY - startY));
        const squareStartX = startX < endX ? startX : startX - squareSize;
        const squareStartY = startY < endY ? startY : startY - squareSize;
        context.strokeRect(squareStartX, squareStartY, squareSize, squareSize);
        break;
        
      case 'rectangle':
        const rectWidth = endX - startX;
        const rectHeight = endY - startY;
        context.strokeRect(startX, startY, rectWidth, rectHeight);
        break;
        
      case 'circle':
        const radiusX = Math.abs(endX - startX) / 2;
        const radiusY = Math.abs(endY - startY) / 2;
        const centerX = startX + (endX - startX) / 2;
        const centerY = startY + (endY - startY) / 2;
        const radius = Math.max(radiusX, radiusY);
        
        context.beginPath();
        context.arc(centerX, centerY, radius, 0, Math.PI * 2);
        context.stroke();
        break;
    }
  }

  updateSettings(settings) {
    console.log('Updating settings:', settings);
    this.tool = settings.tool;
    this.color = settings.color;
    this.size = settings.size;

    if (this.tool === 'eraser') {
      this.ctx.globalCompositeOperation = 'destination-out';
      this.ctx.strokeStyle = 'rgba(0,0,0,1)';
    } else {
      this.ctx.globalCompositeOperation = 'source-over';
      this.ctx.strokeStyle = this.color;
    }
    
    this.ctx.lineWidth = this.size;
    this.ctx.lineCap = 'round';
    this.ctx.lineJoin = 'round';
  }

  toggleDrawing(enabled) {
    console.log('Toggling drawing:', enabled);
    this.isEnabled = enabled;
    this.canvas.style.pointerEvents = enabled ? 'auto' : 'none';
    this.canvas.classList.toggle('active', enabled);
    document.body.classList.toggle('drawing-active', enabled);
    
    if (enabled) {
      this.resizeCanvas();
      // Ensure proper initial settings
      this.updateSettings({
        tool: this.tool,
        color: this.color,
        size: this.size
      });
    }
  }

  clearCanvas() {
    console.log('Clearing canvas');
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}

// Initialize the ScreenWriter
const screenWriter = new ScreenWriter();

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Received message:', message);
  try {
    switch (message.action) {
      case 'toggleDrawing':
        screenWriter.toggleDrawing(message.isDrawing);
        console.log('Drawing toggled:', message.isDrawing);
        break;
      case 'updateSettings':
        screenWriter.updateSettings(message.settings);
        console.log('Settings updated:', message.settings);
        break;
      case 'clearCanvas':
        screenWriter.clearCanvas();
        console.log('Canvas cleared');
        break;
    }
    // Send response to confirm message was handled
    sendResponse({ success: true });
  } catch (error) {
    console.error('Error handling message:', error);
    sendResponse({ success: false, error: error.message });
  }
  return true; // Keep the message channel open for async response
}); 