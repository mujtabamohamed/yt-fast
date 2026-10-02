// YT Speed Controller — Service Worker (background)
// Minimal background script. Keeps the extension operational and handles
// install events. All heavy lifting happens in the content script / popup.

chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason === 'install') {
    // Set the default speed to 1x on first install
    await chrome.storage.local.set({ ytfast_speed: 1 });
  }
});
