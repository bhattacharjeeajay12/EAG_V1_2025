// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  // Set default language preference
  chrome.storage.sync.get(['targetLanguage'], (result) => {
    if (!result.targetLanguage) {
      chrome.storage.sync.set({ targetLanguage: 'hi' });
    }
  });
}); 