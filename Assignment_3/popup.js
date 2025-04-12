document.getElementById('submitBtn').addEventListener('click', async () => {
  const query = document.getElementById('queryInput').value;
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = 'Processing...';

  try {
    // Create a background script to handle the processing
    const response = await chrome.runtime.sendMessage({ action: 'processQuery', query });
    resultDiv.innerHTML = response.result;
  } catch (error) {
    resultDiv.innerHTML = `Error: ${error.message}`;
  }
}); 