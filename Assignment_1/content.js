// Create a floating translation div
const translationDiv = document.createElement('div');
translationDiv.style.cssText = `
  position: fixed;
  padding: 10px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  display: none;
  z-index: 10000;
  max-width: 300px;
  word-wrap: break-word;
`;
document.body.appendChild(translationDiv);

// Function to translate text
async function translateText(text, targetLang) {
  try {
    const response = await fetch(`https://translation.googleapis.com/language/translate/v2?key=YOUR_API_KEY`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        q: text,
        target: targetLang,
        source: 'en'
      })
    });
    
    const data = await response.json();
    return data.data.translations[0].translatedText;
  } catch (error) {
    console.error('Translation error:', error);
    return 'Translation failed. Please try again.';
  }
}

// Handle text selection
document.addEventListener('mouseup', async () => {
  const selectedText = window.getSelection().toString().trim();
  
  if (selectedText) {
    // Get the target language from storage
    chrome.storage.sync.get(['targetLanguage'], async (result) => {
      const targetLang = result.targetLanguage || 'hi'; // Default to Hindi
      
      // Get mouse position
      const selection = window.getSelection();
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      
      // Show loading message
      translationDiv.textContent = 'Translating...';
      translationDiv.style.display = 'block';
      translationDiv.style.left = `${rect.left + window.scrollX}px`;
      translationDiv.style.top = `${rect.bottom + window.scrollY + 5}px`;
      
      // Get translation
      const translatedText = await translateText(selectedText, targetLang);
      translationDiv.textContent = translatedText;
    });
  } else {
    translationDiv.style.display = 'none';
  }
});

// Hide translation div when clicking outside
document.addEventListener('mousedown', (e) => {
  if (e.target !== translationDiv) {
    translationDiv.style.display = 'none';
  }
}); 