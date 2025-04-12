document.addEventListener('DOMContentLoaded', () => {
  const languageSelect = document.getElementById('targetLanguage');
  const statusDiv = document.getElementById('status');

  // Load saved language preference
  chrome.storage.sync.get(['targetLanguage'], (result) => {
    if (result.targetLanguage) {
      languageSelect.value = result.targetLanguage;
    }
  });

  // Save language preference when changed
  languageSelect.addEventListener('change', (e) => {
    const selectedLanguage = e.target.value;
    chrome.storage.sync.set({ targetLanguage: selectedLanguage }, () => {
      statusDiv.textContent = 'Language preference saved!';
      statusDiv.style.display = 'block';
      statusDiv.style.backgroundColor = '#dff0d8';
      setTimeout(() => {
        statusDiv.style.display = 'none';
      }, 2000);
    });
  });
}); 