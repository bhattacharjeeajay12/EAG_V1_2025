// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'processQuery') {
    processQuery(request.query)
      .then(result => sendResponse({ result }))
      .catch(error => sendResponse({ result: 'Error: ' + error.message }));
    return true; // Required for async response
  }
});

async function processQuery(query) {
  try {
    const response = await fetch('http://localhost:5000/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ query }),
      mode: 'cors',
      credentials: 'omit'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server returned ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    return data.result;
  } catch (error) {
    console.error('Error processing query:', error);
    let errorMessage = 'Error processing query:\n';
    errorMessage += `Type: ${error.name}\n`;
    errorMessage += `Message: ${error.message}\n`;
    
    if (error.cause) {
      errorMessage += `Cause: ${error.cause}\n`;
    }
    
    errorMessage += '\nTroubleshooting steps:\n';
    errorMessage += '1. Make sure the Flask server is running (python server.py)\n';
    errorMessage += '2. Check if the server is accessible at http://localhost:5000\n';
    errorMessage += '3. Verify that the server is not blocked by firewall or antivirus\n';
    errorMessage += '4. Ensure all required Python packages are installed (flask, flask-cors)\n';
    errorMessage += '5. Check if the server is running on the correct port (5000)\n';
    errorMessage += '6. Make sure the Python script (talk2mcp-2-UPDATED.py) is in the same directory\n';
    
    throw new Error(errorMessage);
  }
} 