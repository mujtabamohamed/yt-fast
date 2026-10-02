// YT Speed Controller — Firefox Background Script
// Firefox MV2 equivalent of the Chrome service worker.

browser.runtime.onInstalled.addListener(async (details) => {
  if (details.reason === 'install') {
    await browser.storage.local.set({ ytfast_speed: 1 });
  }
});
