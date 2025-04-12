document.addEventListener('DOMContentLoaded', function() {
  const tools = ['pen', 'eraser', 'square', 'rectangle', 'circle'];
  let currentTool = 'pen';
  let isDrawing = false;

  // Tool selection
  tools.forEach(tool => {
    document.getElementById(tool).addEventListener('click', function() {
      document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
      currentTool = tool;
      updateDrawingSettings();
    });
  });   

  // Color picker
  const colorPicker = document.getElementById('color');
  colorPicker.addEventListener('input', updateDrawingSettings);

  // Size slider
  const sizeSlider = document.getElementById('size');
  const sizeValue = document.getElementById('sizeValue');
  sizeSlider.addEventListener('input', function() {
    sizeValue.textContent = this.value + 'px';
    updateDrawingSettings();
  });

  // Toggle drawing
  const toggleButton = document.getElementById('toggleDraw');
  toggleButton.addEventListener('click', function() {
    isDrawing = !isDrawing;
    this.textContent = isDrawing ? 'Stop Drawing' : 'Start Drawing';
    this.style.backgroundColor = isDrawing ? '#ff4444' : '';
    this.style.color = isDrawing ? 'white' : '';
    
    // Query for the active tab
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (!tabs[0]) {
        console.error('No active tab found');
        return;
      }
      
      // Send message to content script
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'toggleDrawing',
        isDrawing: isDrawing
      }, function(response) {
        if (chrome.runtime.lastError) {
          console.error('Error sending message:', chrome.runtime.lastError);
          // Try reinjecting the content script
          chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            files: ['content.js']
          }, function() {
            if (chrome.runtime.lastError) {
              console.error('Error injecting content script:', chrome.runtime.lastError);
            } else {
              // Retry sending the message after script injection
              chrome.tabs.sendMessage(tabs[0].id, {
                action: 'toggleDrawing',
                isDrawing: isDrawing
              });
            }
          });
        }
      });
      
      if (isDrawing) {
        updateDrawingSettings();
      }
    });
  });

  // Clear canvas
  document.getElementById('clear').addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (!tabs[0]) return;
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'clearCanvas'
      }, function(response) {
        if (chrome.runtime.lastError) {
          console.error('Error sending clear message:', chrome.runtime.lastError);
        }
      });
    });
  });

  function updateDrawingSettings() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (!tabs[0]) return;
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'updateSettings',
        settings: {
          tool: currentTool,
          color: colorPicker.value,
          size: parseInt(sizeSlider.value)
        }
      }, function(response) {
        if (chrome.runtime.lastError) {
          console.error('Error sending settings:', chrome.runtime.lastError);
        }
      });
    });
  }
}); 