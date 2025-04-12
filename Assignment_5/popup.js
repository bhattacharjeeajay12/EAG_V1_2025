document.addEventListener('DOMContentLoaded', function() {
  const queryTextarea = document.getElementById('query');
  const submitButton = document.getElementById('submit');
  const resultDiv = document.getElementById('result');
  const loadingDiv = document.getElementById('loading');

  function formatOutput(text) {
    // Split the text into lines
    const lines = text.split('\n');
    let formattedHTML = '';
    let inLogSection = false;
    
    lines.forEach(line => {
      if (line.includes('📋 Execution Summary:')) {
        formattedHTML += `<div class="summary"><strong>${line}</strong></div>`;
      } else if (line.includes('📜 Log Output:')) {
        inLogSection = true;
        formattedHTML += `<div class="log-section"><strong>${line}</strong></div>`;
      } else if (line.trim() === '-------------------') {
        formattedHTML += `<hr>`;
      } else if (inLogSection) {
        // Format log entries
        if (line.includes('🔧 Tool Called:')) {
          formattedHTML += `<div class="tool-output">${line}</div>`;
        } else if (line.includes('📝 Reasoning:')) {
          formattedHTML += `<div class="tool-output">${line}</div>`;
        } else if (line.includes('✅ Result:')) {
          formattedHTML += `<div class="tool-output success">${line}</div>`;
        } else if (line.includes('❌ Error:')) {
          formattedHTML += `<div class="tool-output error">${line}</div>`;
        } else if (line.includes('📜')) {
          // Format log messages
          const logType = line.includes('[ERROR]') ? 'error' : 
                         line.includes('[WARNING]') ? 'warning' : 'info';
          formattedHTML += `<div class="log-entry log-${logType}">${line}</div>`;
        } else {
          formattedHTML += `<div>${line}</div>`;
        }
      } else {
        formattedHTML += `<div>${line}</div>`;
      }
    });
    
    return formattedHTML;
  }

  submitButton.addEventListener('click', async function() {
    const query = queryTextarea.value.trim();
    if (!query) {
      resultDiv.textContent = 'Please enter a query';
      return;
    }

    // Show loading indicator
    loadingDiv.style.display = 'block';
    resultDiv.innerHTML = '';

    try {
      // Send message to background script
      const response = await chrome.runtime.sendMessage({
        action: 'processQuery',
        query: query
      });

      // Format and display the result
      resultDiv.innerHTML = formatOutput(response.result);
    } catch (error) {
      resultDiv.innerHTML = `<div class="tool-output error">Error: ${error.message}</div>`;
    } finally {
      loadingDiv.style.display = 'none';
    }
  });
}); 